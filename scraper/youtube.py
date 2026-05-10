import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
BASE_URL = "https://www.googleapis.com/youtube/v3"

def _get(endpoint, params):
    """Helper: GET request to YouTube Data API v3."""
    params["key"] = YOUTUBE_API_KEY
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_youtube_resources(topic, difficulty, recency_filter):
    """
    Fetches top 10 YouTube videos for a given topic and filters.
    Uses YouTube Data API v3 via plain requests (no google-api-python-client needed).
    """
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY in ("your_key_here", ""):
        print("[!] YouTube API Key missing. Skipping YouTube.")
        return []

    try:
        # Determine publishedAfter based on recency filter
        published_after = None
        now = datetime.utcnow()
        if recency_filter == "1":   # Past week
            published_after = (now - timedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif recency_filter == "2": # Past month
            published_after = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        elif recency_filter == "3": # Past year
            published_after = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")

        search_query = f"{topic} tutorial" if difficulty == "All" else f"{topic} tutorial {difficulty}"

        # 1. Search for videos
        search_params = {
            "q": search_query,
            "part": "id,snippet",
            "maxResults": 10,
            "type": "video",
            "order": "relevance",
        }
        if published_after:
            search_params["publishedAfter"] = published_after

        search_data = _get("search", search_params)
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
        if not video_ids:
            return []

        # 2. Get detailed video stats
        video_data = _get("videos", {
            "id": ",".join(video_ids),
            "part": "snippet,statistics,contentDetails",
        })

        # Collect unique channel IDs for credibility lookup
        channel_ids = list({item["snippet"]["channelId"] for item in video_data.get("items", [])})
        channel_data = _get("channels", {
            "id": ",".join(channel_ids),
            "part": "statistics",
        })
        channel_subs = {
            ch["id"]: int(ch["statistics"].get("subscriberCount", 0))
            for ch in channel_data.get("items", [])
        }

        resources = []
        for item in video_data.get("items", []):
            snippet = item["snippet"]
            stats   = item.get("statistics", {})
            content = item.get("contentDetails", {})

            resources.append({
                "title":            snippet["title"],
                "url":              f"https://www.youtube.com/watch?v={item['id']}",
                "thumbnail":        snippet["thumbnails"].get("high", {}).get("url", ""),
                "source_name":      "YouTube",
                "type":             "video",
                "published_at":     snippet["publishedAt"],
                "channel_name":     snippet["channelTitle"],
                "view_count":       int(stats.get("viewCount", 0)),
                "like_count":       int(stats.get("likeCount", 0)),
                "duration":         content.get("duration", "PT0M"),
                "subscriber_count": channel_subs.get(snippet["channelId"], 0),
                "difficulty":       difficulty,
            })

        return resources

    except Exception as e:
        print(f"[!] YouTube Error: {e}")
        return []
