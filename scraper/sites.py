import requests
from datetime import datetime
import re

def get_site_resources(topic):
    """
    Scrapes study sites for a given topic using reliable APIs and RSS feeds.
    """
    resources = []
    clean_topic = topic.lower().replace(" ", "")

    # 1. DEV.to (Using official JSON API - very reliable)
    try:
        dev_url = f"https://dev.to/api/articles?tag={clean_topic}&per_page=5"
        resp = requests.get(dev_url, timeout=10)
        if resp.status_code == 200:
            for item in resp.json():
                resources.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "source_name": "DEV.to",
                    "type": "article",
                    "published_at": item.get("published_timestamp", datetime.now().isoformat())
                })
    except Exception as e:
        print(f"[!] DEV.to Error: {e}")

    # 2. freeCodeCamp (Using RSS Feed for the tag - no JS required)
    from bs4 import BeautifulSoup
    try:
        fcc_url = f"https://www.freecodecamp.org/news/tag/{clean_topic}/rss/"
        resp = requests.get(fcc_url, timeout=10)
        if resp.status_code == 200:
            import warnings
            from bs4 import XMLParsedAsHTMLWarning
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            
            # Parse XML. Since we use html.parser, tags will be lowercase.
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.find_all("item")
            for item in items[:5]:
                title = item.find("title")
                link = item.find("link")
                pubdate = item.find("pubdate")
                
                if title:
                    # html.parser handles <link>http...</link> sometimes as text, sometimes as next sibling
                    url_text = link.text.strip() if link and link.text else ""
                    if not url_text and link and link.next_sibling:
                        url_text = str(link.next_sibling).strip()
                        
                    if "http" in url_text:
                        resources.append({
                            "title": title.text.replace("<![CDATA[", "").replace("]]>", "").strip(),
                            "url": url_text,
                            "source_name": "freeCodeCamp",
                            "type": "article",
                            "published_at": pubdate.text if pubdate else datetime.now().isoformat()
                        })
    except Exception as e:
        print(f"[!] freeCodeCamp Error: {e}")

    return resources
