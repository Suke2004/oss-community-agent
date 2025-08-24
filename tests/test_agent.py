# tests/test_agent.py

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from apps.agent.main import run_oss_agent, reddit_tool, rag_tool

class TestAgent(unittest.TestCase):
    """Test cases for the main agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_subreddit = "testpython"
        self.test_query = "python installation"
        self.test_submission_id = "test123"
        
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('apps.agent.main.portia')
    def test_run_oss_agent_success(self, mock_portia):
        """Test successful agent run"""
        # Mock Portia response
        mock_run_state = MagicMock()
        mock_run_state.status.value = "completed"
        mock_run_state.get_variable.side_effect = lambda x: {
            "selected_post_id": "test_post_123",
            "selected_post_title": "Test Question",
            "drafted_reply": "Test reply",
            "moderation_report": {"is_flagged": False},
            "clarification_response": {"action": "approve"},
            "reddit_post_result": {"status": "success"}
        }.get(x)
        
        mock_portia.run_plan.return_value = mock_run_state
        
        # Run agent
        result = run_oss_agent(
            query=self.test_query,
            subreddit=self.test_subreddit
        )
        
        # Assertions
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["selected_post_id"], "test_post_123")
        self.assertIn("drafted_reply", result)
        self.assertIn("moderation_report", result)
    
    @patch('apps.agent.main.portia')
    def test_run_oss_agent_failure(self, mock_portia):
        """Test agent run with failure"""
        # Mock Portia failure
        mock_run_state = MagicMock()
        mock_run_state.status.value = "failed"
        mock_run_state.error_message = "Test error"
        
        mock_portia.run_plan.return_value = mock_run_state
        
        # Run agent
        result = run_oss_agent(
            query=self.test_query,
            subreddit=self.test_subreddit
        )
        
        # Assertions
        self.assertEqual(result["status"], "failed")
        self.assertIn("error", result)
    
    def test_run_oss_agent_with_submission_id(self):
        """Test agent run with specific submission ID"""
        with patch('apps.agent.main.portia') as mock_portia:
            # Mock successful response
            mock_run_state = MagicMock()
            mock_run_state.status.value = "completed"
            mock_run_state.get_variable.side_effect = lambda x: {
                "selected_post_id": self.test_submission_id,
                "selected_post_title": "Specific Test Question",
                "drafted_reply": "Specific test reply",
                "moderation_report": {"is_flagged": False},
                "clarification_response": {"action": "approve"},
                "reddit_post_result": {"status": "success"}
            }.get(x)
            
            mock_portia.run_plan.return_value = mock_run_state
            
            # Run agent with submission ID
            result = run_oss_agent(
                query=self.test_query,
                subreddit=self.test_subreddit,
                submission_id=self.test_submission_id
            )
            
            # Assertions
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["selected_post_id"], self.test_submission_id)
    
    @patch('apps.agent.main.portia')
    def test_run_oss_agent_exception_handling(self, mock_portia):
        """Test agent exception handling"""
        # Mock Portia to raise exception
        mock_portia.run_plan.side_effect = Exception("Test exception")
        
        # Run agent
        result = run_oss_agent(
            query=self.test_query,
            subreddit=self.test_subreddit
        )
        
        # Assertions
        self.assertEqual(result["status"], "failed")
        self.assertIn("error", result)
        self.assertIn("Test exception", result["error"])

class TestAgentConfiguration(unittest.TestCase):
    """Test agent configuration and initialization"""
    
    def test_reddit_tool_initialization(self):
        """Test Reddit tool initialization"""
        # This test verifies the tool can be imported and initialized
        self.assertIsNotNone(reddit_tool)
    
    def test_rag_tool_initialization(self):
        """Test RAG tool initialization"""
        # This test verifies the tool can be imported and initialized
        self.assertIsNotNone(rag_tool)
    
    @patch.dict(os.environ, {
        'REDDIT_CLIENT_ID': 'test_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USERNAME': 'test_user',
        'REDDIT_PASSWORD': 'test_pass'
    })
    def test_environment_variables(self):
        """Test environment variable loading"""
        from apps.agent.main import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
        self.assertEqual(REDDIT_CLIENT_ID, 'test_id')
        self.assertEqual(REDDIT_CLIENT_SECRET, 'test_secret')

if __name__ == '__main__':
    unittest.main()
