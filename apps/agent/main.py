# apps/agent/main.py

import os
import json
import logging
import uuid
import time
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Import Portia AI SDK components (with fallback to mock)
try:
    from portia import Portia, PlanBuilder, Clarification
    from portia.models import ToolCall, PlanRunState, PlanRunStatus
    from portia.tool_registry import PortiaToolRegistry
    print("✅ Using real Portia SDK")
except ImportError:
    print("⚠️ Portia SDK not available, using mock implementation")
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from mock_portia import Portia, PlanBuilder, Clarification, ToolCall, PlanRunState, PlanRunStatus, PortiaToolRegistry

# Import your custom tools
from tools.reddit_tool import RedditTool
from tools.rag_tool import RAGTool
from tools.moderation_tools import analyze_text as ModerationTool_analyze_text

# --- Configuration & Logging ---
load_dotenv() # Load environment variables from .env file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize API keys and settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true" # Default to dry run

# Ensure LLM API keys are available based on provider
if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables when using OpenAI provider.")
elif LLM_PROVIDER == "groq" and not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables when using Groq provider.")
elif LLM_PROVIDER == "ollama":
    logging.info("Using Ollama provider - no API key required (assuming local installation).")
elif LLM_PROVIDER == "none":
    logging.warning("LLM provider set to 'none' - agent will run without LLM capabilities.")
else:
    logging.warning(f"Unknown LLM provider '{LLM_PROVIDER}' - defaulting to keyword-only responses.")

# Ensure Reddit API credentials are available
if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET or not REDDIT_USERNAME or not REDDIT_PASSWORD:
    raise ValueError("Reddit API credentials (CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD) not found in environment variables.")

# --- Tool Initialization ---
# Initialize your custom tools
reddit_tool = RedditTool(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent="oss-community-agent/0.1 (by u/BennyPerumalla)" # IMPORTANT: Use your Reddit username
)
rag_tool = RAGTool()

# --- Portia Initialization ---
# Initialize Portia with your API key
portia = Portia(api_key=os.getenv("PORTIA_API_KEY"))

# Create a custom tool registry for Portia
# This allows Portia to recognize and call your custom Python functions
custom_tool_registry = PortiaToolRegistry()
custom_tool_registry.register_tool(
    name="search_reddit_questions",
    description="Searches a specified subreddit for questions matching keywords.",
    func=reddit_tool.search_questions,
    input_schema={
        "type": "object",
        "properties": {
            "subreddit_name": {"type": "string", "description": "The name of the subreddit to search (e.g., 'python')."},
            "keywords": {"type": "string", "description": "Keywords to search for within the subreddit."},
            "limit": {"type": "integer", "description": "Maximum number of posts to retrieve."}
        },
        "required": ["subreddit_name", "keywords"]
    }
)
custom_tool_registry.register_tool(
    name="draft_reply_from_docs",
    description="Retrieves relevant documentation and drafts a reply to a user's question with citations.",
    func=rag_tool.retrieve_and_generate,
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The user's question to answer."},
        },
        "required": ["query"]
    }
)
custom_tool_registry.register_tool(
    name="moderate_text_for_issues",
    description="Analyzes text for profanity, PII, or other flagged content.",
    func=ModerationTool_analyze_text,
    input_schema={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The text content to moderate."}
        },
        "required": ["text"]
    }
)
custom_tool_registry.register_tool(
    name="post_reddit_reply",
    description="Posts a reply to a specific Reddit submission.",
    func=reddit_tool.post_reply,
    input_schema={
        "type": "object",
        "properties": {
            "submission_id": {"type": "string", "description": "The ID of the Reddit submission to reply to."},
            "reply_text": {"type": "string", "description": "The content of the reply."}
        },
        "required": ["submission_id", "reply_text"]
    }
)


# --- Agent Core Logic ---

def run_oss_agent(query: str, subreddit: str, submission_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Runs the OSS Community Auto-Responder agent.

    This function defines the agent's plan and executes it using Portia.
    It includes steps for searching Reddit, drafting replies, moderation,
    human-in-the-loop clarification, and posting.

    Args:
        query (str): The initial user query or topic for the agent.
        subreddit (str): The subreddit to monitor or post to.
        submission_id (Optional[str]): If provided, the agent will attempt to reply to this specific submission.
                                        Otherwise, it will search for new questions.

    Returns:
        Dict[str, Any]: A dictionary containing the final status and output of the agent run.
    """
    run_id = str(uuid.uuid4())
    start_time = time.time()
    logging.info(f"[{run_id}] Agent initiated with query: '{query}' on subreddit: '{subreddit}'.")
    logging.info(f"[{run_id}] Dry Run Mode: {DRY_RUN}.")

    try:
        # 1. Define the Agent's Plan
        plan_builder = PlanBuilder(
            name="OSS Community Auto-Responder Plan",
            description="Automates drafting and posting replies to Reddit questions.",
            tools=custom_tool_registry.get_all_tools()
        )

        # Step 1: Search Reddit for relevant questions
        plan_builder.add_step(
            name="search_reddit_questions_step",
            tool_call=ToolCall(
                name="search_reddit_questions",
                args={"subreddit_name": subreddit, "keywords": query, "limit": 5}
            ),
            output_variable="reddit_posts"
        )

        # Step 2: Draft a reply using the RAG tool
        plan_builder.add_step(
            name="draft_reply",
            tool_call=ToolCall(
                name="draft_reply_from_docs",
                args={"query": f"{query} on subreddit {subreddit}"}
            ),
            output_variable="drafted_reply"
        )

        # Step 3: Moderate the drafted reply
        plan_builder.add_step(
            name="moderate_draft",
            tool_call=ToolCall(
                name="moderate_text_for_issues",
                args={"text": "{{drafted_reply}}"}
            ),
            output_variable="moderation_report"
        )

        # Step 4: Human-in-the-loop clarification
        plan_builder.add_step(
            name="request_human_clarification",
            tool_call=Clarification(
                message=(
                    "An AI-drafted reply is ready for your review for Reddit query "
                    f"**'{query}'** on subreddit **'{subreddit}'**.\n\n"
                    "**Moderation Report:**\n```json\n{{moderation_report}}\n```\n\n"
                    "**Proposed Reply:**\n```\n{{drafted_reply}}\n```\n\n"
                    "Please approve, edit, or reject this reply."
                ),
                expected_response_schema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["approve", "reject", "edit"]},
                        "edited_reply": {"type": "string", "description": "The human-edited version of the reply (if 'edit' action).", "default": ""},
                        "reason": {"type": "string", "description": "Optional reason for action."}
                    },
                    "required": ["action"]
                }
            ),
            output_variable="clarification_response"
        )

        # Step 5: Handle clarification response
        plan_builder.add_step(
            name="handle_clarification_response",
            description="Process the human clarification response.",
            code_block="""
if clarification_response.get('action') == 'approve':
    reddit_post_result = {'status': 'approved', 'message': 'Reply approved by human.'}
elif clarification_response.get('action') == 'reject':
    reddit_post_result = {'status': 'rejected', 'message': 'Reply rejected by human.'}
elif clarification_response.get('action') == 'edit':
    reddit_post_result = {'status': 'edited', 'message': 'Reply edited by human.'}
else:
    reddit_post_result = {'status': 'unknown', 'message': 'Unknown action.'}
            """,
            input_variables=["clarification_response"],
            output_variables=["reddit_post_result"]
        )

        # 2. Compile and Run the Plan
        plan = plan_builder.build()
        logging.info(f"[{run_id}] Portia Plan created successfully.")

        # Execute the plan
        plan_run_state = portia.run_plan(plan=plan, initial_input={})

        # Log the final status
        logging.info(f"[{run_id}] Agent run finished with status: {plan_run_state.status}.")
        if plan_run_state.status == PlanRunStatus.FAILED:
            logging.error(f"[{run_id}] Error details: {plan_run_state.error_message}", exc_info=True)
            return {"status": "failed", "error": plan_run_state.error_message}
        
        final_output = {
            "status": plan_run_state.status.value,
            "selected_post_id": plan_run_state.get_variable("selected_post_id"),
            "selected_post_title": plan_run_state.get_variable("selected_post_title"),
            "drafted_reply": plan_run_state.get_variable("drafted_reply"),
            "moderation_report": plan_run_state.get_variable("moderation_report"),
            "clarification_response": plan_run_state.get_variable("clarification_response"),
            "reddit_post_result": plan_run_state.get_variable("reddit_post_result"),
            "total_duration_sec": round(time.time() - start_time, 2)
        }
        logging.info(f"[{run_id}] Final Output: {json.dumps(final_output, indent=2)}")
        return final_output

    except Exception as e:
        logging.error(f"[{run_id}] An unexpected fatal error occurred.", exc_info=True)
        return {"status": "failed", "error": f"An unexpected fatal error occurred: {e}"}

# --- Main execution for testing/demonstration ---
if __name__ == "__main__":
    print("--- Running Agent: Search for general query ---")
    result_general_search = run_oss_agent(query="Portia AI installation", subreddit="learnpython")
    print("\n" + "="*80 + "\n")