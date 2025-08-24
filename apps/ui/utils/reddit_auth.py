# utils/reddit_auth.py
import praw

def test_reddit_auth(creds: dict) -> dict:
    """
    Test Reddit API authentication using provided credentials.
    
    Args:
        creds (dict): Dictionary with keys:
            - client_id
            - client_secret
            - username
            - password
            - user_agent
    
    Returns:
        dict: {
            "valid": bool,
            "username": str | None,
            "errors": str | None
        }
    """
    try:
        reddit = praw.Reddit(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            username=creds["username"],
            password=creds["password"],
            user_agent=creds["user_agent"],
        )
        
        # Try fetching current user
        me = reddit.user.me()
        if me:
            return {"valid": True, "username": str(me), "errors": None}
        else:
            return {"valid": False, "username": None, "errors": "Authentication failed (no user)"}
    
    except Exception as e:
        return {"valid": False, "username": None, "errors": str(e)}
