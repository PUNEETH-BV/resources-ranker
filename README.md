# 🚀 ResourceRank

**ResourceRank** is an automated, AI-inspired tool that helps you find the highest-quality learning resources on any topic across the internet. Instead of endlessly scrolling through Google or YouTube, ResourceRank scrapes multiple platforms, scores the resources based on community engagement and relevance, and generates a beautiful, responsive HTML dashboard for you to study from.

## ✨ Features
- **Multi-Platform Scraping:** Automatically pulls tutorials, articles, and videos from **YouTube**, **DEV.to**, **Medium**, and **freeCodeCamp**.
- **Smart Scoring Engine:** Uses a custom algorithm to rank resources based on views, likes, claps, reading time, and more.
- **Filtering System:** Filter results by Content Type (Videos vs. Articles), Difficulty, Recency, and Price (Free vs. Paid).
- **Beautiful UI Dashboard:** Generates a stunning, interactive HTML file with modern glassmorphism design, filter buttons, and detailed score breakdowns.

---

## 🛠️ Technologies Used
- **Python 3:** The core logic language.
- **BeautifulSoup4 & lxml:** For parsing XML/RSS feeds and HTML.
- **Requests:** For fetching JSON APIs and RSS feeds without relying on heavy headless browsers.
- **Jinja2:** For injecting the Python data into the beautiful HTML templates.
- **Rich:** For the beautiful and interactive command-line interface (CLI).
- **Vanilla HTML/CSS/JS:** Used in `template.html` for a completely standalone, lightning-fast dashboard frontend.

---

## ⚙️ How It Works
1. **Scraping Layer (`/scraper`):** 
   - `youtube.py`: Uses the official YouTube Data API v3.
   - `sites.py`: Hits the DEV.to public JSON API and parses the freeCodeCamp RSS feed.
   - `medium.py`: Parses the Medium tags RSS feed to bypass Cloudflare/JS restrictions.
   - `reddit.py`: Uses PRAW to fetch top discussions (optional).
2. **Scoring Layer (`/ranker/scorer.py`):** 
   - Each resource is passed through a scoring algorithm out of 100 points based on platform-specific metrics (e.g., YouTube views/likes ratio, Medium claps, or DEV.to recent publication dates).
3. **Presentation Layer (`main.py` & `template.html`):** 
   - The resources are sorted by score, passed through Jinja2, and rendered into a beautiful UI inside the `output/` folder.

---

## 🚀 Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/PUNEETH-BV/resources-ranker.git
cd resources-ranker
```

### 2. Install Dependencies
Make sure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a file named `.env` in the root folder and add your API keys:
```env
# Required for Video Search
YOUTUBE_API_KEY=your_youtube_api_key_here

# Optional (Set to "skip" to disable Reddit scraping)
REDDIT_CLIENT_ID=skip
REDDIT_CLIENT_SECRET=skip
REDDIT_USER_AGENT=ResourceRank/1.0
```

*(You can get a free YouTube API key from the [Google Cloud Console](https://console.cloud.google.com/).)*

---

## 🎮 How to Use

Simply run the main script from your terminal:
```bash
python main.py
```

The CLI will prompt you for:
1. **Topic** (e.g., "Python for beginners" or "Solar System")
2. **Content Type** (Videos, Articles, or Both)
3. **Difficulty**
4. **Recency**

Once the scraping and scoring are complete, the tool will generate a file like `results_python_for_beginners_20260510.html` inside the `output/` folder. Open this file in any web browser to see your customized dashboard!

---

## 🤝 Contributing
Feel free to open issues or submit pull requests. If you want to add a new scraper (like Hashnode or Coursera), simply create a new file in the `/scraper` folder and add its scoring logic to `/ranker/scorer.py`!
