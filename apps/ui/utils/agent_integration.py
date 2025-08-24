# apps/ui/utils/agent_integration.py

import sys
import os
import uuid
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
import json

# Add the parent directories to path to import the existing agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.database import DatabaseManager

class AgentIntegration:
    """
    Integration layer between the Streamlit UI and the existing Portia agent backend.
    This class provides a bridge to interact with the agent while maintaining UI responsiveness.
    """
    
    def __init__(self):
        self.db = DatabaseManager()
        self.agent_status = "idle"
        self.current_runs = {}
        self.last_heartbeat = datetime.now()
        
        # Initialize mock agent state for demo
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize some demo data for the UI to display"""
        
        # Create some sample requests for demonstration
        sample_requests = [
            {
                'id': str(uuid.uuid4()),
                'subreddit': 'learnpython',
                'post_id': 'sample_001',
                'post_title': 'How do I install Python on Windows?',
                'post_content': 'I\'m new to programming and want to install Python on my Windows 10 computer. Can someone guide me through the process?',
                'post_author': 'pythonbeginner123',
                'post_url': 'https://reddit.com/r/learnpython/sample_001',
                'status': 'pending',
                'drafted_reply': 'To install Python on Windows, you can follow these steps:\n\n1. Go to python.org\n2. Download the latest Python installer\n3. Run the installer and check "Add Python to PATH"\n4. Verify installation by opening Command Prompt and typing `python --version`\n\nThis should get you started with Python development on Windows!',
                'moderation_score': 0.1,
                'agent_confidence': 0.85,
                'citations': json.dumps([
                    {'title': 'Python Installation Guide', 'source': 'python.org'},
                    {'title': 'Windows Setup Documentation', 'source': 'docs.python.org'}
                ]),
                'processing_time': 2.3
            },
            {
                'id': str(uuid.uuid4()),
                'subreddit': 'django',
                'post_id': 'sample_002',
                'post_title': 'Django models vs SQLAlchemy - which is better?',
                'post_content': 'I\'m starting a new web project and wondering whether to use Django ORM or SQLAlchemy. What are the pros and cons?',
                'post_author': 'webdev_curious',
                'post_url': 'https://reddit.com/r/django/sample_002',
                'status': 'pending',
                'drafted_reply': 'Both Django ORM and SQLAlchemy are excellent choices, but they serve different purposes:\n\n**Django ORM:**\n- Integrated with Django framework\n- Convention over configuration\n- Great for rapid development\n- Active Record pattern\n\n**SQLAlchemy:**\n- Framework agnostic\n- More flexible and powerful\n- Data Mapper pattern\n- Better for complex queries\n\nChoose Django ORM if you\'re building a Django app, SQLAlchemy for more flexibility.',
                'moderation_score': 0.05,
                'agent_confidence': 0.92,
                'citations': json.dumps([
                    {'title': 'Django ORM Documentation', 'source': 'docs.djangoproject.com'},
                    {'title': 'SQLAlchemy Tutorial', 'source': 'sqlalchemy.org'}
                ]),
                'processing_time': 3.1
            },
            {
                'id': str(uuid.uuid4()),
                'subreddit': 'python',
                'post_id': 'sample_003',
                'post_title': 'Understanding Python decorators',
                'post_content': 'Can someone explain Python decorators in simple terms? I keep seeing @ symbols in code and don\'t understand what they do.',
                'post_author': 'decorator_confused',
                'post_url': 'https://reddit.com/r/python/sample_003',
                'status': 'approved',
                'drafted_reply': 'Python decorators are a way to modify or extend functions without changing their code directly.\n\nThink of it like wrapping a gift:\n- The function is the gift\n- The decorator is the wrapping paper\n- The @ symbol applies the wrapping\n\nHere\'s a simple example:\n\n```python\n@my_decorator\ndef say_hello():\n    print("Hello!")\n```\n\nThe decorator can add functionality before, after, or around the original function.',
                'final_reply': 'Python decorators are a way to modify or extend functions without changing their code directly.\n\nThink of it like wrapping a gift:\n- The function is the gift\n- The decorator is the wrapping paper\n- The @ symbol applies the wrapping\n\nHere\'s a simple example:\n\n```python\n@my_decorator\ndef say_hello():\n    print("Hello!")\n```\n\nThe decorator can add functionality before, after, or around the original function.',
                'moderation_score': 0.02,
                'agent_confidence': 0.78,
                'citations': json.dumps([
                    {'title': 'Python Decorators Guide', 'source': 'realpython.com'},
                    {'title': 'Decorator Documentation', 'source': 'docs.python.org'}
                ]),
                'processing_time': 1.8
            }
        ]
        
        # Add sample requests to database
        for request in sample_requests:
            try:
                self.db.add_request(request)
            except Exception as e:
                # Request might already exist, that's okay for demo
                pass
    
    def start_agent_monitoring(self, subreddit: str, keywords: str = "") -> str:
        """
        Start monitoring a subreddit for new questions.
        Returns a run ID for tracking the operation.
        """
        
        run_id = str(uuid.uuid4())
        
        # In a real implementation, this would start the actual Portia agent
        # For demo purposes, we'll simulate the process
        
        self.current_runs[run_id] = {
            'type': 'monitoring',
            'status': 'running',
            'subreddit': subreddit,
            'keywords': keywords,
            'start_time': datetime.now(),
            'posts_found': 0,
            'replies_drafted': 0
        }
        
        # Simulate the monitoring process in a separate thread
        thread = threading.Thread(target=self._simulate_monitoring, args=(run_id, subreddit, keywords))
        thread.daemon = True
        thread.start()
        
        return run_id
    
    def _simulate_monitoring(self, run_id: str, subreddit: str, keywords: str):
        """Simulate the agent monitoring process"""
        
        try:
            # Simulate finding posts
            time.sleep(2)
            self.current_runs[run_id]['posts_found'] = 3
            self.current_runs[run_id]['status'] = 'processing'
            
            # Simulate drafting replies
            time.sleep(3)
            self.current_runs[run_id]['replies_drafted'] = 2
            
            # Mark as completed
            time.sleep(1)
            self.current_runs[run_id]['status'] = 'completed'
            self.current_runs[run_id]['end_time'] = datetime.now()
            
        except Exception as e:
            self.current_runs[run_id]['status'] = 'failed'
            self.current_runs[run_id]['error'] = str(e)
    
    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific agent run"""
        return self.current_runs.get(run_id)
    
    def get_all_active_runs(self) -> List[Dict[str, Any]]:
        """Get all currently active agent runs"""
        active_runs = []
        for run_id, run_data in self.current_runs.items():
            if run_data['status'] in ['running', 'processing']:
                run_data['id'] = run_id
                active_runs.append(run_data)
        return active_runs
    
    def stop_agent_run(self, run_id: str) -> bool:
        """Stop a specific agent run"""
        if run_id in self.current_runs:
            self.current_runs[run_id]['status'] = 'stopped'
            return True
        return False
    
    def process_single_request(self, query: str, subreddit: str, submission_id: Optional[str] = None) -> str:
        """
        Process a single request using the agent.
        Returns a run ID for tracking.
        """
        
        run_id = str(uuid.uuid4())
        
        # In a real implementation, this would call the existing agent main function
        # from apps.agent.main import run_oss_agent
        # result = run_oss_agent(query, subreddit, submission_id)
        
        # For demo purposes, simulate the process
        self.current_runs[run_id] = {
            'type': 'single_request',
            'status': 'running',
            'query': query,
            'subreddit': subreddit,
            'submission_id': submission_id,
            'start_time': datetime.now()
        }
        
        # Simulate processing in a separate thread
        thread = threading.Thread(target=self._simulate_single_request, args=(run_id, query, subreddit))
        thread.daemon = True
        thread.start()
        
        return run_id
    
    def _simulate_single_request(self, run_id: str, query: str, subreddit: str):
        """Simulate processing a single request"""
        
        try:
            # Simulate the agent workflow
            time.sleep(1)
            self.current_runs[run_id]['status'] = 'searching'
            
            time.sleep(2)
            self.current_runs[run_id]['status'] = 'drafting'
            
            time.sleep(2)
            self.current_runs[run_id]['status'] = 'moderating'
            
            time.sleep(1)
            self.current_runs[run_id]['status'] = 'completed'
            self.current_runs[run_id]['end_time'] = datetime.now()
            
            # Create a mock request for this process
            mock_request = {
                'id': str(uuid.uuid4()),
                'subreddit': subreddit,
                'post_id': f'generated_{int(time.time())}',
                'post_title': query[:100] + '...' if len(query) > 100 else query,
                'post_content': f'Generated request based on query: {query}',
                'post_author': 'simulated_user',
                'post_url': f'https://reddit.com/r/{subreddit}/simulated',
                'status': 'pending',
                'drafted_reply': f'This is a simulated response to: {query}\n\nThe agent would generate a comprehensive answer here based on the documentation and RAG system.',
                'moderation_score': 0.15,
                'agent_confidence': 0.75,
                'citations': json.dumps([
                    {'title': 'Simulated Documentation', 'source': 'docs.example.com'},
                ]),
                'processing_time': 4.0
            }
            
            self.db.add_request(mock_request)
            
        except Exception as e:
            self.current_runs[run_id]['status'] = 'failed'
            self.current_runs[run_id]['error'] = str(e)
    
    def get_agent_health(self) -> Dict[str, Any]:
        """Get current agent health status"""
        
        # Simulate system health checks
        return {
            'status': 'healthy',
            'uptime': '2h 45m',
            'last_heartbeat': self.last_heartbeat,
            'memory_usage': 67,
            'cpu_usage': 23,
            'reddit_api_status': 'connected',
            'rag_system_status': 'ready',
            'database_status': 'healthy',
            'active_runs': len(self.get_all_active_runs()),
            'total_requests_today': len(self.db.get_requests_by_filter({'limit': 1000})),
            'pending_approvals': len(self.db.get_pending_requests())
        }
    
    def update_heartbeat(self):
        """Update the agent heartbeat timestamp"""
        self.last_heartbeat = datetime.now()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get detailed system performance metrics"""
        
        # In a real implementation, this would gather actual system metrics
        return {
            'response_times': {
                'avg_24h': 3.2,
                'p95_24h': 8.1,
                'p99_24h': 15.3
            },
            'success_rates': {
                'overall': 94.2,
                'last_hour': 96.8,
                'last_24h': 93.5
            },
            'api_usage': {
                'reddit_calls_today': 247,
                'llm_calls_today': 89,
                'llm_provider': os.getenv('LLM_PROVIDER', 'openai').lower(),
                'rate_limit_remaining': 92
            },
            'database_stats': {
                'total_requests': 1456,
                'total_approved': 987,
                'total_rejected': 234,
                'pending': len(self.db.get_pending_requests())
            }
        }
    
    def trigger_manual_scan(self, subreddit: str, keywords: str = "") -> str:
        """Trigger a manual scan of a subreddit"""
        return self.start_agent_monitoring(subreddit, keywords)
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current agent configuration"""
        
        # In a real implementation, this would read from the actual config
        return {
            'dry_run_mode': True,
            'auto_approval': False,
            'confidence_threshold': 0.7,
            'scan_interval': 5,
            'max_requests_per_hour': 20,
            'monitored_subreddits': ['python', 'learnpython', 'django'],
            'moderation_enabled': True,
            'moderation_threshold': 0.5
        }
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update agent configuration"""
        
        # In a real implementation, this would update the actual config
        # For demo purposes, just return True
        return True

# Singleton instance for use throughout the UI
agent_integration = AgentIntegration()
