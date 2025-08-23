# tools/reddit_tool.py

import os
import praw
import time
from typing import List, Dict, Any, Optional

class RedditTool:
    """
    A robust and modular tool for interacting with the Reddit API.

    This class encapsulates all Reddit-related functionality, including
    authentication, searching for posts, and posting replies. It is
    designed to be resilient to network issues and API rate limits.
    """

    def __init__(self, client_id: str, client_secret: str, username: str, password: str, user_agent: str):
        """
        Initializes the Reddit tool with API credentials and a user agent.

        Args:
            client_id (str): The Reddit application client ID.
            client_secret (str): The Reddit application client secret.
            username (str): The Reddit account username for authentication.
            password (str): The Reddit account password.
            user_agent (str): A unique, descriptive user agent string as required by Reddit.
        """
        if not all([client_id, client_secret, username, password, user_agent]):
            raise ValueError("All Reddit credentials and user_agent must be provided.")
        
        # Use PRAW's built-in authentication for security
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )
        print("Reddit instance created and authenticated.")

    def search_questions(self, subreddit_name: str, keywords: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches a subreddit for posts that match the given keywords.

        Args:
            subreddit_name (str): The name of the subreddit (e.g., 'python').
            keywords (str): The keywords to search for.
            limit (int): The maximum number of posts to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                   represents a post with key details.
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Using .search() for a query-based search
            search_results = subreddit.search(query=keywords, limit=limit)
            
            posts = []
            for submission in search_results:
                posts.append({
                    "id": submission.id,
                    "title": submission.title,
                    "url": submission.url,
                    "created_utc": submission.created_utc,
                    "selftext": submission.selftext if hasattr(submission, 'selftext') else ''
                })
            
            print(f"Found {len(posts)} relevant posts in r/{subreddit_name}.")
            return posts

        except praw.exceptions.PRAWException as e:
            print(f"PRAW error during search: {e}", file=os.sys.stderr)
            # TODO: Implement exponential backoff for rate limits.
            return []
        except Exception as e:
            print(f"An unexpected error occurred during search: {e}", file=os.sys.stderr)
            return []

    def post_reply(self, submission_id: str, reply_text: str) -> Dict[str, Any]:
        """
        Posts a reply to a specific Reddit submission.

        Args:
            submission_id (str): The ID of the Reddit submission to reply to.
            reply_text (str): The content of the reply message.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the reply.
        """
        try:
            # Get the submission object by its ID
            submission = self.reddit.submission(id=submission_id)
            
            # Check if the bot has already replied to avoid spamming
            # This is a good practice to avoid duplicate replies on the same post.
            has_replied = any(c.author and c.author.name == self.reddit.user.me().name for c in submission.comments)
            
            if has_replied:
                return {"status": "skipped", "message": "Already replied to this post."}

            reply_object = submission.reply(reply_text)
            
            print(f"Successfully replied to post ID: {submission_id}")
            return {
                "status": "success",
                "message": "Reply posted.",
                "reply_id": reply_object.id,
                "submission_id": submission_id
            }

        except praw.exceptions.RedditAPIException as e:
            # Handle API errors, such as rate limits or invalid submission IDs
            print(f"Reddit API error while posting: {e}", file=os.sys.stderr)
            # TODO: Add logic to handle different API exceptions, like rate limits.
            return {"status": "error", "message": str(e)}
        except Exception as e:
            print(f"An unexpected error occurred while posting: {e}", file=os.sys.stderr)
            return {"status": "error", "message": str(e)}

# --- For local testing/demonstration ---
# This block is for testing the tool in isolation
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Use dummy credentials if not available for a quick test
    try:
        reddit_tool = RedditTool(
            client_id=os.getenv("REDDIT_CLIENT_ID", "dummy_id"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET", "dummy_secret"),
            username=os.getenv("REDDIT_USERNAME", "dummy_user"),
            password=os.getenv("REDDIT_PASSWORD", "dummy_pass"),
            user_agent="oss-community-agent/0.1 (by u/TestUser)"
        )

        # Example 1: Search for a post
        print("--- Searching for posts ---")
        posts = reddit_tool.search_questions(subreddit_name="learnpython", keywords="Python 3.11", limit=2)
        print("Search Results:")
        for post in posts:
            print(f"- Title: {post['title']} (ID: {post['id']})")
        
        # Example 2: Post a dummy reply (requires a real submission ID and proper credentials)
        # Note: This will not work with dummy credentials
        # print("\n--- Posting a reply (Dry Run) ---")
        # dummy_id = "1b8p6m5"
        # reply_text = "Hello from the test bot! This is an example reply."
        # result = reddit_tool.post_reply(submission_id=dummy_id, reply_text=reply_text)
        # print("Post Result:", result)

    except ValueError as e:
        print(f"Could not initialize RedditTool: {e}")