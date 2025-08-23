# apps/agent/main.py

import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Import Portia AI SDK components
from portia import Portia, PlanBuilder, Clarification
from portia.models import ToolCall, PlanRunState, PlanRunStatus
from portia.tool_registry import PortiaToolRegistry

# Import your custom tools
from tools.reddit_tool import RedditTool
from tools.rag_tool import RAGTool
from tools.moderation_tool import analyze_text as ModerationTool_analyze_text

# --- Configuration ---
load_dotenv() # Load environment variables from .env file

# Initialize API keys and settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # For RAGTool's LLM
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true" # Default to dry run

# Ensure essential API keys are available
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")
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
    print(f"Agent initiated with query: '{query}' on subreddit: '{subreddit}'")
    print(f"Dry Run Mode: {DRY_RUN}")

    # 1. Define the Agent's Plan
    # The PlanBuilder allows us to define the steps of the agent's workflow.
    # Each step uses a registered tool or a Portia native function like Clarification.
    plan_builder = PlanBuilder(
        name="OSS Community Auto-Responder Plan",
        description="Automates drafting and posting replies to Reddit questions.",
        tools=custom_tool_registry.get_all_tools() # Register all custom tools
    )

    # Step 1: Search Reddit for relevant questions
    # TODO: For a production system, this would be triggered by a webhook
    #       or a scheduled job monitoring new posts, not a manual search.
    plan_builder.add_step(
        name="search_reddit_questions_step",
        tool_call=ToolCall(
            name="search_reddit_questions",
            args={"subreddit_name": subreddit, "keywords": query, "limit": 5}
        ),
        output_variable="reddit_posts"
    )

    # Step 2: Select a specific post to reply to (if not provided)
    # This is a simple selection logic for the demo.
    # TODO: Implement more sophisticated logic for selecting the best post
    #       (e.g., filtering by age, comment count, existing replies).
    plan_builder.add_step(
        name="select_post_to_reply",
        description="Selects the most relevant Reddit post to reply to.",
        code_block=f"""
if '{submission_id}' != 'None':
    selected_post_id = '{submission_id}'
    selected_post_title = 'User-specified submission'
    selected_post_body = 'N/A'
else:
    posts = {{plan_run.reddit_posts}}
    if not posts:
        print("No relevant Reddit posts found.")
        selected_post_id = None
        selected_post_title = None
        selected_post_body = None
    else:
        # For demo, just pick the first one
        selected_post = posts[0]
        selected_post_id = selected_post.get('id')
        selected_post_title = selected_post.get('title')
        selected_post_body = selected_post.get('selftext', '')
        print(f"Selected post: {{selected_post_title}} (ID: {{selected_post_id}})")

plan_run.selected_post_id = selected_post_id
plan_run.selected_post_title = selected_post_title
plan_run.selected_post_body = selected_post_body
        """,
        input_variables=["reddit_posts"],
        output_variables=["selected_post_id", "selected_post_title", "selected_post_body"]
    )

    # Conditional step: Only proceed if a post was selected
    plan_builder.add_conditional_step(
        name="check_if_post_selected",
        condition="plan_run.selected_post_id is not None",
        steps=[
            # Step 3: Draft a reply using the RAG tool
            plan_builder.add_step(
                name="draft_reply",
                tool_call=ToolCall(
                    name="draft_reply_from_docs",
                    args={"query": "{{plan_run.selected_post_title}} {{plan_run.selected_post_body}}"}
                ),
                output_variable="drafted_reply"
            ),

            # Step 4: Moderate the drafted reply
            plan_builder.add_step(
                name="moderate_draft",
                tool_call=ToolCall(
                    name="moderate_text_for_issues",
                    args={"text": "{{plan_run.drafted_reply}}"}
                ),
                output_variable="moderation_report"
            ),

            # Step 5: Human-in-the-loop clarification
            # This is where the agent pauses for human approval.
            plan_builder.add_step(
                name="request_human_clarification",
                tool_call=Clarification(
                    message=(
                        "An AI-drafted reply is ready for your review for Reddit post "
                        f"**'{{plan_run.selected_post_title}}'** (ID: {{plan_run.selected_post_id}}).\n\n"
                        f"**Moderation Report:**\n```json\n{{json.dumps(plan_run.moderation_report, indent=2)}}\n```\n\n"
                        "**Proposed Reply:**\n```\n{{plan_run.drafted_reply}}\n```\n\n"
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
            ),

            # Conditional Step: Handle clarification response
            plan_builder.add_conditional_step(
                name="handle_clarification_response",
                condition="plan_run.clarification_response.get('action') == 'approve'",
                steps=[
                    # Step 6: Post the reply to Reddit (only if not in dry run mode)
                    plan_builder.add_conditional_step(
                        name="post_reply_to_reddit",
                        condition=f"not {DRY_RUN}", # Only run if DRY_RUN is False
                        steps=[
                            plan_builder.add_step(
                                name="execute_post_reddit_reply",
                                tool_call=ToolCall(
                                    name="post_reddit_reply",
                                    args={
                                        "submission_id": "{{plan_run.selected_post_id}}",
                                        "reply_text": "{{plan_run.clarification_response.get('edited_reply') or plan_run.drafted_reply}}"
                                    }
                                ),
                                output_variable="reddit_post_result"
                            )
                        ],
                        else_steps=[
                            plan_builder.add_step(
                                name="dry_run_post_simulation",
                                description="Simulating Reddit post in dry run mode.",
                                code_block="plan_run.reddit_post_result = {'status': 'simulated_success', 'message': 'Post simulated successfully in dry run mode.'}"
                            )
                        ]
                    )
                ],
                else_steps=[
                    plan_builder.add_step(
                        name="handle_rejected_or_edited_reply",
                        description="Human rejected or edited the reply. No automated post.",
                        code_block="""
if plan_run.clarification_response.get('action') == 'reject':
    print(f"Reply rejected by human: {{plan_run.clarification_response.get('reason', 'No reason provided')}}")
elif plan_run.clarification_response.get('action') == 'edit':
    print(f"Reply edited by human. Original: '{{plan_run.drafted_reply}}', Edited: '{{plan_run.clarification_response.get('edited_reply')}}'")
    # TODO: Potentially re-run moderation on edited reply or log the changes.
plan_run.reddit_post_result = {'status': 'skipped', 'message': 'Post skipped due to human intervention.'}
                        """
                    )
                ]
            )
        ],
        else_steps=[
            plan_builder.add_step(
                name="no_post_action",
                description="No action taken as no relevant post was selected.",
                code_block="print('No relevant Reddit post found to process.')"
            )
        ]
    )


    # 2. Compile and Run the Plan
    plan = plan_builder.build()
    print("Portia Plan created successfully.")

    # Execute the plan
    # TODO: Implement robust error handling for plan execution.
    #       Consider retries for transient errors.
    plan_run_state = portia.run_plan(plan=plan, initial_input={})

    # Log the final status
    print(f"\nAgent run finished with status: {plan_run_state.status}")
    if plan_run_state.status == PlanRunStatus.FAILED:
        print(f"Error details: {plan_run_state.error_message}")
        return {"status": "failed", "error": plan_run_state.error_message}
    
    final_output = {
        "status": plan_run_state.status.value,
        "selected_post_id": plan_run_state.get_variable("selected_post_id"),
        "selected_post_title": plan_run_state.get_variable("selected_post_title"),
        "drafted_reply": plan_run_state.get_variable("drafted_reply"),
        "moderation_report": plan_run_state.get_variable("moderation_report"),
        "clarification_response": plan_run_state.get_variable("clarification_response"),
        "reddit_post_result": plan_run_state.get_variable("reddit_post_result")
    }
    print(f"Final Output: {json.dumps(final_output, indent=2)}")
    return final_output

# --- Main execution for testing/demonstration ---
if __name__ == "__main__":
    # Example usage:
    # To test, ensure your .env file has all required API keys
    # and your data/corpus has some .md files.

    # Example 1: Search for a general query
    print("--- Running Agent: Search for general query ---")
    result_general_search = run_oss_agent(query="Portia AI installation", subreddit="learnpython")
    print("\n" + "="*80 + "\n")

    # Example 2: Reply to a specific submission (replace with a real ID from your search)
    # You would typically get this submission_id from a monitoring process.
    # For a quick test, you can manually find a post ID on Reddit.
    # print("--- Running Agent: Reply to specific submission ---")
    # specific_submission_id = "your_reddit_submission_id_here" # e.g., "1j3k4l"
    # result_specific_reply = run_oss_agent(query="Portia AI installation", subreddit="learnpython", submission_id=specific_submission_id)
    # print("\n" + "="*80 + "\n")