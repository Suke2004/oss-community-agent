import os
import praw

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="agent-approval-dashboard/0.1"
)

def get_subreddit_data(subreddit_name: str, limit: int = 5):
    """Fetch top hot posts from a subreddit"""
    try:
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.hot(limit=limit):
            posts.append({
                "title": post.title,
                "score": post.score,
                "url": f"https://reddit.com{post.permalink}",
                "author": str(post.author) if post.author else "Unknown",
                "created_utc": post.created_utc
            })
        return posts
    except Exception as e:
        return {"error": str(e)}
