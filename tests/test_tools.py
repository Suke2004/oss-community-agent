# tests/test_tools.py

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.reddit_tool import RedditTool
from tools.rag_tool import RAGTool
from tools.moderation_tools import analyze_text

class TestRedditTool(unittest.TestCase):
    """Test cases for Reddit tool functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_credentials = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'username': 'test_username',
            'password': 'test_password',
            'user_agent': 'test_agent/1.0'
        }
        
    @patch('tools.reddit_tool.praw')
    def test_reddit_tool_initialization(self, mock_praw):
        """Test Reddit tool initialization"""
        # Mock PRAW Reddit instance
        mock_reddit = MagicMock()
        mock_praw.Reddit.return_value = mock_reddit
        
        # Initialize tool
        reddit_tool = RedditTool(**self.test_credentials)
        
        # Assertions
        self.assertIsNotNone(reddit_tool)
        mock_praw.Reddit.assert_called_once()
    
    @patch('tools.reddit_tool.praw')
    def test_search_questions_success(self, mock_praw):
        """Test successful search for questions"""
        # Mock PRAW components
        mock_reddit = MagicMock()
        mock_subreddit = MagicMock()
        mock_submission = MagicMock()
        
        # Configure mock submission
        mock_submission.id = "test_post_123"
        mock_submission.title = "Test Question"
        mock_submission.url = "https://reddit.com/test"
        mock_submission.created_utc = 1234567890
        mock_submission.selftext = "Test question content"
        
        # Configure mock subreddit
        mock_subreddit.search.return_value = [mock_submission]
        mock_reddit.subreddit.return_value = mock_subreddit
        
        mock_praw.Reddit.return_value = mock_reddit
        
        # Initialize tool and search
        reddit_tool = RedditTool(**self.test_credentials)
        result = reddit_tool.search_questions("python", "installation", 5)
        
        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "test_post_123")
        self.assertEqual(result[0]["title"], "Test Question")
    
    @patch('tools.reddit_tool.praw')
    def test_search_questions_empty_result(self, mock_praw):
        """Test search with empty results"""
        # Mock PRAW components
        mock_reddit = MagicMock()
        mock_subreddit = MagicMock()
        
        # Configure mock subreddit to return empty results
        mock_subreddit.search.return_value = []
        mock_reddit.subreddit.return_value = mock_subreddit
        
        mock_praw.Reddit.return_value = mock_reddit
        
        # Initialize tool and search
        reddit_tool = RedditTool(**self.test_credentials)
        result = reddit_tool.search_questions("nonexistent", "query", 5)
        
        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    @patch('tools.reddit_tool.praw')
    def test_post_reply_success(self, mock_praw):
        """Test successful posting of reply"""
        # Mock PRAW components
        mock_reddit = MagicMock()
        mock_submission = MagicMock()
        mock_comment = MagicMock()
        
        # Configure mock submission and comment
        mock_submission.comments = [mock_comment]
        mock_comment.author = None  # No previous reply from bot
        mock_reddit.user.me.return_value.name = "test_username"
        mock_reddit.submission.return_value = mock_submission
        
        mock_praw.Reddit.return_value = mock_reddit
        
        # Initialize tool and post reply
        reddit_tool = RedditTool(**self.test_credentials)
        result = reddit_tool.post_reply("test_post_123", "Test reply content")
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)
    
    def test_reddit_tool_missing_credentials(self):
        """Test Reddit tool initialization with missing credentials"""
        with self.assertRaises(ValueError):
            RedditTool(
                client_id="",
                client_secret="test_secret",
                username="test_user",
                password="test_pass",
                user_agent="test_agent"
            )

class TestRAGTool(unittest.TestCase):
    """Test cases for RAG tool functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.rag_tool = RAGTool()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_rag_tool_initialization(self):
        """Test RAG tool initialization"""
        self.assertIsNotNone(self.rag_tool)
    
    @patch('tools.rag_tool.Chroma')
    def test_retrieve_and_generate_success(self, mock_chroma):
        """Test successful retrieval and generation"""
        # Mock ChromaDB response
        mock_docs = [
            MagicMock(page_content="Test document content", metadata={"source": "test.md"})
        ]
        mock_chroma.side_effect = MagicMock()
        
        # Test retrieval
        result = self.rag_tool.retrieve_and_generate("test query")
        
        # Assertions
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_rag_tool_with_empty_query(self):
        """Test RAG tool with empty query"""
        result = self.rag_tool.retrieve_and_generate("")
        
        # Should return a default response
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

class TestModerationTool(unittest.TestCase):
    """Test cases for moderation tool functionality"""
    
    def test_analyze_text_clean(self):
        """Test analysis of clean text"""
        clean_text = "This is a clean text with no issues."
        result = analyze_text(clean_text)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("is_flagged", result)
        self.assertIn("flags", result)
        self.assertFalse(result["is_flagged"])
        self.assertEqual(len(result["flags"]), 0)
    
    def test_analyze_text_with_profanity(self):
        """Test analysis of text with profanity"""
        profane_text = "This text contains some inappropriate language."
        result = analyze_text(profane_text)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("is_flagged", result)
        self.assertIn("flags", result)
    
    def test_analyze_text_with_pii(self):
        """Test analysis of text with PII"""
        pii_text = "My email is test@example.com and phone is 555-123-4567"
        result = analyze_text(pii_text)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("is_flagged", result)
        self.assertIn("flags", result)
    
    def test_analyze_text_with_sensitive_keywords(self):
        """Test analysis of text with sensitive keywords"""
        sensitive_text = "This contains personal information and private details"
        result = analyze_text(sensitive_text)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("is_flagged", result)
        self.assertIn("flags", result)
    
    def test_analyze_text_empty(self):
        """Test analysis of empty text"""
        result = analyze_text("")
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("is_flagged", result)
        self.assertIn("flags", result)
    
    def test_analyze_text_none(self):
        """Test analysis of None text"""
        result = analyze_text(None)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn("is_flagged", result)
        self.assertIn("flags", result)

class TestToolIntegration(unittest.TestCase):
    """Test cases for tool integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('tools.reddit_tool.praw')
    def test_full_workflow_simulation(self, mock_praw):
        """Test full workflow simulation"""
        # Mock Reddit tool
        mock_reddit = MagicMock()
        mock_praw.Reddit.return_value = mock_reddit
        
        reddit_tool = RedditTool(
            client_id="test",
            client_secret="test",
            username="test",
            password="test",
            user_agent="test"
        )
        
        # Mock RAG tool
        rag_tool = RAGTool()
        
        # Test workflow
        # 1. Search Reddit
        search_result = reddit_tool.search_questions("python", "help", 1)
        self.assertIsInstance(search_result, list)
        
        # 2. Generate response
        response = rag_tool.retrieve_and_generate("Python installation help")
        self.assertIsInstance(response, str)
        
        # 3. Moderate response
        moderation_result = analyze_text(response)
        self.assertIsInstance(moderation_result, dict)
        
        # 4. Post reply (simulated)
        if not moderation_result.get("is_flagged", False):
            post_result = reddit_tool.post_reply("test_post", response)
            self.assertIsInstance(post_result, dict)

if __name__ == '__main__':
    unittest.main()
