# mock_portia.py
"""
Enhanced Mock implementation of Portia SDK for Python 3.10 compatibility.
This allows the agent to run without the actual Portia SDK while maintaining the interface.
"""

import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Portia:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.run_id = str(uuid.uuid4())[:8]
        logger.info(f"[MOCK-{self.run_id}] Portia initialized with API key: {'Set' if api_key else 'Not set'}")
    
    def run_plan(self, plan, initial_input=None):
        logger.info(f"[MOCK-{self.run_id}] Running plan: {plan.name}")
        start_time = time.time()
        
        try:
            # Simulate plan execution with realistic timing
            time.sleep(0.5)  # Simulate processing time
            
            # Mock plan execution result
            class MockPlanRunState:
                def __init__(self, run_id):
                    self.run_id = run_id
                    self.status = PlanRunStatus.COMPLETED
                    self.error_message = None
                    self.start_time = start_time
                    self.end_time = time.time()
                    self._variables = {
                        "reddit_posts": [
                            {
                                "id": f"mock_post_{run_id}",
                                "title": "Sample Reddit Question about Python",
                                "selftext": "I'm having trouble with my Python code. Can anyone help?",
                                "url": f"https://reddit.com/r/learnpython/comments/mock_post_{run_id}",
                                "created_utc": time.time() - 3600
                            }
                        ],
                        "selected_post_id": f"mock_post_{run_id}",
                        "selected_post_title": "Sample Reddit Question about Python",
                        "selected_post_body": "I'm having trouble with my Python code. Can anyone help?",
                        "drafted_reply": """Based on your question, here's a helpful response:

**Solution:**
Your issue can be resolved by following these steps:

1. First, ensure you have the correct Python version installed
2. Check your environment variables
3. Verify your dependencies are properly installed

**Code Example:**
```python
# Your code here
import sys
print(f"Python version: {sys.version}")
```

**Additional Resources:**
- [Python Documentation](https://docs.python.org/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/python)

Let me know if you need any clarification!""",
                        "moderation_report": {
                            "is_flagged": False,
                            "flags": [],
                            "safety_score": 0.95,
                            "confidence": 0.9
                        },
                        "clarification_response": {
                            "action": "approve",
                            "reason": "Response looks good and helpful",
                            "edited_reply": None
                        },
                        "reddit_post_result": {
                            "status": "simulated_success",
                            "message": "Post simulated successfully in dry run mode",
                            "post_id": f"mock_reply_{run_id}",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                
                def get_variable(self, name):
                    return self._variables.get(name)
                
                def get_all_variables(self):
                    return self._variables.copy()
            
            result = MockPlanRunState(self.run_id)
            logger.info(f"[MOCK-{self.run_id}] Plan execution completed successfully in {time.time() - start_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"[MOCK-{self.run_id}] Plan execution failed: {str(e)}")
            class MockPlanRunState:
                def __init__(self, run_id, error):
                    self.run_id = run_id
                    self.status = PlanRunStatus.FAILED
                    self.error_message = str(error)
                    self._variables = {}
                
                def get_variable(self, name):
                    return None
                
                def get_all_variables(self):
                    return {}
            
            return MockPlanRunState(self.run_id, e)

class PlanBuilder:
    def __init__(self, name=None, description=None, tools=None):
        self.name = name
        self.description = description
        self.tools = tools or []
        self.steps = []
        logger.info(f"[MOCK] PlanBuilder created: {name}")
    
    def add_step(self, name=None, tool_call=None, output_variable=None, description=None, code_block=None, input_variables=None, output_variables=None):
        step = {
            "name": name,
            "tool_call": tool_call,
            "output_variable": output_variable,
            "description": description,
            "code_block": code_block,
            "input_variables": input_variables,
            "output_variables": output_variables,
            "type": "step"
        }
        self.steps.append(step)
        logger.info(f"[MOCK] Added step: {name}")
        return step
    
    def add_conditional_step(self, name=None, condition=None, steps=None, else_steps=None):
        conditional_step = {
            "name": name,
            "condition": condition,
            "steps": steps or [],
            "else_steps": else_steps or [],
            "type": "conditional"
        }
        self.steps.append(conditional_step)
        logger.info(f"[MOCK] Added conditional step: {name}")
        return conditional_step
    
    def build(self):
        logger.info(f"[MOCK] Built plan with {len(self.steps)} steps")
        return MockPlan(self.name, self.steps)

class MockPlan:
    def __init__(self, name, steps):
        self.name = name
        self.steps = steps
        self.created_at = datetime.now()

class Clarification:
    def __init__(self, message=None, expected_response_schema=None):
        self.message = message
        self.expected_response_schema = expected_response_schema
        self.clarification_id = str(uuid.uuid4())[:8]
        logger.info(f"[MOCK] Clarification created (ID: {self.clarification_id}) with message length: {len(message) if message else 0}")
    
    def get_message(self):
        return self.message
    
    def get_schema(self):
        return self.expected_response_schema

class ToolCall:
    def __init__(self, name=None, args=None):
        self.name = name
        self.args = args or {}
        self.call_id = str(uuid.uuid4())[:8]
        logger.info(f"[MOCK] ToolCall created (ID: {self.call_id}): {name} with args: {json.dumps(args, default=str) if args else '{}'}")

class PlanRunState:
    pass

class PlanRunStatus:
    COMPLETED = "completed"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"

class PortiaToolRegistry:
    def __init__(self):
        self.tools = {}
        logger.info("[MOCK] PortiaToolRegistry initialized")
    
    def register_tool(self, name, description, func, input_schema=None):
        self.tools[name] = {
            "name": name,
            "description": description,
            "func": func,
            "input_schema": input_schema
        }
        logger.info(f"[MOCK] Registered tool: {name}")
    
    def get_all_tools(self):
        return list(self.tools.values())
    
    def get_tool(self, name):
        return self.tools.get(name)
    
    def list_tools(self):
        return list(self.tools.keys())

# Enhanced utility functions for better mock behavior
def create_mock_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a realistic mock response"""
    return {
        "status": "success",
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "mock": True
    }

def simulate_processing_delay(min_delay: float = 0.1, max_delay: float = 0.5):
    """Simulate realistic processing delays"""
    import random
    time.sleep(random.uniform(min_delay, max_delay))
