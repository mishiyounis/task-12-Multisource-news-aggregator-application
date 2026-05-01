                                Multi-Source News Aggregator

A Python application that fetches real-time news from multiple RSS feeds (BBC, CNN, TechCrunch, The Verge, Reuters, ESPN, Variety) and displays them in a structured format with categories, search, trending news, and save functionality.

Features:

- Fetch news from 7+ RSS feeds automatically
- Auto-categorize news into General, Technology, Business, Sports, Entertainment
- Filter news by category or source
- Search news by keywords
- Trending news detection based on keywords and source popularity
- Auto-refresh every 60 seconds (optional)
- Save news to JSON or CSV for offline reading
- View saved news with delete options (single, multiple, or all)
- Double-click any news to open original article in browser
- Modern GUI interface with tabs (News, Trending, Saved)

News Sources:

- BBC News
- CNN
- TechCrunch
- The Verge
- Reuters Business
- ESPN
- Variety

Categories:

- General
- Technology
- Business
- Sports
- Entertainment
- Trending (auto-detected)

Requirements:

- Python 3.7 or higher
- customtkinter
- feedparser
- requests

Installation:

pip install customtkinter feedparser requests

How to Run:

python news_aggregator.py

How to Use:

1. Launch the application
2. Click "Fetch Latest News" to get news from all RSS feeds
3. Use category radio buttons to filter by category
4. Use source dropdown to filter by news source
5. Enter keyword and click "Search" to find specific news
6. Enable "Auto Refresh" for automatic updates every 60 seconds
7. Click "Save Current News" to save displayed news
8. Go to "Saved" tab to view saved news
9. Double-click any news to open original article
10. Use Delete buttons to remove saved news

