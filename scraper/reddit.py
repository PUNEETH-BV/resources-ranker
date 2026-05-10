import os
import praw
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "ResourceRank/1.0")

def get_reddit_resources(topic, recency_filter):
    """
    Fetches top 10 Reddit posts for a given topic and filters.
    """
    if not REDDIT_CLIENT_ID or REDDIT_CLIENT_ID in ("your_id_here", "skip"):
        print("[!] Reddit credentials set to 'skip'. Skipping Reddit.")
        return []

    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

        # Basic subreddit mapping
        subreddits = ["learnpython", "datascience", "MachineLearning", "learnprogramming", "cscareerquestions"]
        
        # Determine best subreddit or search all
        search_query = topic
        time_filter = "all"
        if recency_filter == "1": time_filter = "week"
        elif recency_filter == "2": time_filter = "month"
        elif recency_filter == "3": time_filter = "year"

        resources = []
        # Search across the preferred subreddits
        combined_subs = "+".join(subreddits)
        for post in reddit.subreddit(combined_subs).search(search_query, sort="relevance", time_filter=time_filter, limit=10):
            resources.append({
                "title": post.title,
                "url": f"https://www.reddit.com{post.permalink}",
                "source_name": "Reddit",
                "type": "article", # Reddit posts are text/link based
                "upvotes": post.score,
                "upvote_ratio": post.upvote_ratio,
                "comment_count": post.num_comments,
                "published_at": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                "subreddit": post.subreddit.display_name
            })

        return resources

    except Exception as e:
        print(f"[!] Reddit Error: {e}")
        return []
