import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_medium_resources(topic):
    """
    Scrapes Medium for a given topic using its RSS feed to avoid JavaScript blocks.
    """
    resources = []
    # Medium tags use hyphens, e.g. "machine-learning"
    clean_topic = topic.lower().replace(" ", "-")
    url = f"https://medium.com/feed/tag/{clean_topic}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            import warnings
            from bs4 import XMLParsedAsHTMLWarning
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.find_all("item")
            
            for item in items[:10]:
                title = item.find("title")
                link = item.find("link")
                
                # html.parser handles namespaces by dropping them or lowercasing
                creator = item.find("dc:creator")
                if not creator:
                    creator = item.find("creator")
                    
                pubdate = item.find("pubdate")
                
                if title:
                    # Parse link correctly
                    url_text = link.text.strip() if link and link.text else ""
                    if not url_text and link and link.next_sibling:
                        url_text = str(link.next_sibling).strip()

                    if "http" in url_text:
                        resources.append({
                            "title": title.text.replace("<![CDATA[", "").replace("]]>", "").strip(),
                            "url": url_text,
                            "source_name": "Medium",
                            "type": "article",
                            "claps": 0, # RSS doesn't provide claps
                            "reading_time": 5, # default estimate
                            "author": creator.text if creator else "Unknown",
                            "published_at": pubdate.text if pubdate else datetime.now().isoformat()
                        })
    except Exception as e:
        print(f"[!] Medium Error: {e}")

    return resources
