import re
from datetime import datetime

def calculate_recency_points(published_at, max_pts):
    """
    Calculates points based on recency.
    <1 month = 100%, <6 months = 75%, <1 year = 50%, older = 25%
    """
    try:
        # Normalize published_at to datetime
        if isinstance(published_at, str):
            # Try to parse ISO format
            dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        else:
            dt = published_at
            
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days < 30: return max_pts
        if diff.days < 180: return int(max_pts * 0.75)
        if diff.days < 365: return int(max_pts * 0.5)
        return int(max_pts * 0.25)
    except:
        return int(max_pts * 0.5)

def score_youtube(item):
    """
    YouTube scoring (Max 100):
    - Views (25): log scale
    - Likes (20): log scale
    - Recency (20)
    - Credibility (20): sub count
    - Duration (15): 5-30m = 15, 30-60m = 10, else 5
    """
    points = {}
    
    # Views (25)
    views = item.get("view_count", 0)
    if views >= 1000000: points["Views"] = 25
    elif views >= 100000: points["Views"] = 15
    elif views >= 10000: points["Views"] = 8
    else: points["Views"] = 4

    # Likes (20)
    likes = item.get("like_count", 0)
    if likes >= 50000: points["Likes"] = 20
    elif likes >= 5000: points["Likes"] = 12
    elif likes >= 500: points["Likes"] = 6
    else: points["Likes"] = 2

    # Recency (20)
    points["Recency"] = calculate_recency_points(item.get("published_at"), 20)

    # Credibility (20)
    subs = item.get("subscriber_count", 0)
    if subs >= 100000: points["Credibility"] = 20
    elif subs >= 10000: points["Credibility"] = 15
    else: points["Credibility"] = 10

    # Duration (15)
    # duration is ISO 8601 (e.g., PT15M)
    duration_str = item.get("duration", "PT0M")
    mins = 0
    match = re.search(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration_str)
    if match:
        h = int(match.group(1)) if match.group(1) else 0
        m = int(match.group(2)) if match.group(2) else 0
        mins = h * 60 + m
    
    if 5 <= mins <= 30: points["Duration"] = 15
    elif 30 < mins <= 60: points["Duration"] = 10
    else: points["Duration"] = 5

    total = sum(points.values())
    return total, points

def score_reddit(item):
    """
    Reddit scoring (Max 100):
    - Upvotes (30): log scale
    - Upvote ratio (25): ratio * 25
    - Comments (20): 500+ = 20, 100 = 12, 10 = 5
    - Recency (25)
    """
    points = {}
    
    # Upvotes (30)
    upvotes = item.get("upvotes", 0)
    if upvotes >= 10000: points["Upvotes"] = 30
    elif upvotes >= 1000: points["Upvotes"] = 20
    elif upvotes >= 100: points["Upvotes"] = 10
    else: points["Upvotes"] = 5

    # Ratio (25)
    points["Upvote Ratio"] = int(item.get("upvote_ratio", 0.5) * 25)

    # Comments (20)
    comments = item.get("comment_count", 0)
    if comments >= 500: points["Comments"] = 20
    elif comments >= 100: points["Comments"] = 12
    elif comments >= 10: points["Comments"] = 5
    else: points["Comments"] = 2

    # Recency (25)
    points["Recency"] = calculate_recency_points(item.get("published_at"), 25)

    total = sum(points.values())
    return total, points

def score_medium(item):
    """
    Medium scoring (Max 100):
    - Claps (35): log scale
    - Recency (25)
    - Reading time (20): 5-15m = 20, else scale down
    - Author (20): default 10
    """
    points = {}
    
    # Claps (35)
    claps = item.get("claps", 0)
    if claps >= 10000: points["Claps"] = 35
    elif claps >= 1000: points["Claps"] = 25
    elif claps >= 100: points["Claps"] = 15
    else: points["Claps"] = 5

    # Recency (25)
    points["Recency"] = calculate_recency_points(item.get("published_at"), 25)

    # Reading time (20)
    rt = item.get("reading_time", 0)
    if 5 <= rt <= 15: points["Reading Time"] = 20
    elif rt > 0: points["Reading Time"] = 10
    else: points["Reading Time"] = 5

    # Author (20)
    points["Author Credibility"] = 10 if item.get("author") == "Unknown" else 20

    total = sum(points.values())
    return total, points

def score_site(item, topic):
    """
    Study sites scoring (Max 100):
    - Site Credibility (40): FCC=40, GFG=35, DEV=30
    - Recency (35)
    - Title Relevance (25): keyword matches
    """
    points = {}
    
    # Credibility (40)
    name = item.get("source_name")
    if name == "freeCodeCamp": points["Site Credibility"] = 40
    elif name == "GeeksforGeeks": points["Site Credibility"] = 35
    elif name == "DEV.to": points["Site Credibility"] = 30
    else: points["Site Credibility"] = 20

    # Recency (35)
    points["Recency"] = calculate_recency_points(item.get("published_at"), 35)

    # Relevance (25)
    title = item.get("title", "").lower()
    matches = title.count(topic.lower())
    points["Title Relevance"] = min(25, matches * 10)

    total = sum(points.values())
    return total, points

def rank_resources(resources, topic):
    """
    Scores and ranks all resources.
    """
    ranked = []
    for item in resources:
        source = item["source_name"]
        if source == "YouTube":
            score, breakdown = score_youtube(item)
            stats = {
                "Views": f"{item.get('view_count', 0):,}",
                "Likes": f"{item.get('like_count', 0):,}",
                "Channel": item.get("channel_name", "Unknown")
            }
        elif source == "Reddit":
            score, breakdown = score_reddit(item)
            stats = {
                "Upvotes": item.get("upvotes", 0),
                "Comments": item.get("comment_count", 0),
                "Subreddit": item.get("subreddit", "Unknown")
            }
        elif source == "Medium":
            score, breakdown = score_medium(item)
            stats = {
                "Claps": f"{item.get('claps', 0):,}",
                "Read Time": f"{item.get('reading_time', 0)} min",
                "Author": item.get("author", "Unknown")
            }
        else: # Study sites
            score, breakdown = score_site(item, topic)
            stats = {
                "Source": item.get("source_name", "Unknown")
            }
        
        item["score"] = score
        item["breakdown"] = breakdown
        item["stats"] = stats
        ranked.append(item)

    # Sort by score descending
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
