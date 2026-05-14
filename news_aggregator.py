import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import requests
import json
import csv
import feedparser
from datetime import datetime
import threading
import time
import os
import webbrowser

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class NewsAggregator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Multi-Source News Aggregator")
        self.root.geometry("1200x700")
        self.root.minsize(1200, 700)
        
    
        self.api_key = "Add your API_KEY"  
        
        # Categories with their keywords
        self.categories = {
            "General": ["general"],
            "Technology": ["technology", "tech", "software", "ai", "coding", "programming", "developer", "app", "digital", "computer", "internet"],
            "Business": ["business", "finance", "economy", "market", "stock", "company", "startup", "investment", "trade", "bank"],
            "Sports": ["sports", "football", "cricket", "basketball", "tennis", "olympic", "match", "game", "player", "team", "world cup"],
            "Entertainment": ["entertainment", "movie", "film", "music", "celebrity", "hollywood", "bollywood", "tv", "series", "netflix"]
        }
        
        self.categories_display = ["All", "General", "Technology", "Business", "Sports", "Entertainment", "Trending"]
        
        self.rss_feeds = {
            "BBC News": {"url": "http://feeds.bbci.co.uk/news/rss.xml", "category": "General"},
            "CNN": {"url": "http://rss.cnn.com/rss/edition.rss", "category": "General"},
            "TechCrunch": {"url": "https://techcrunch.com/feed/", "category": "Technology"},
            "The Verge": {"url": "https://www.theverge.com/rss/index.xml", "category": "Technology"},
            "Reuters Business": {"url": "https://www.reutersagency.com/feed/?best-topics=business&post_type=best", "category": "Business"},
            "ESPN": {"url": "https://www.espn.com/espn/rss/news", "category": "Sports"},
            "Variety": {"url": "https://variety.com/feed/", "category": "Entertainment"}
        }
        
        self.news_data = []
        self.filtered_data = []
        self.trending_news = []
        self.saved_news = []
        self.saved_file = "saved_news.json"
        self.auto_refresh = False
        self.refresh_interval = 60  # seconds
        
        # Load saved news
        self.load_saved_news()
        
        self.setup_ui()
        self.fetch_news()
        self.root.mainloop()
    
    def setup_ui(self):
        main = ctk.CTkFrame(self.root, fg_color="#f0f2f5")
        main.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        header = ctk.CTkFrame(main, corner_radius=12, height=80, fg_color="#1e40af")
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="Multi-Source News Aggregator", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=(15, 5))
        ctk.CTkLabel(header, text="News from NewsAPI and RSS Feeds | Auto Refresh | Trending News", font=ctk.CTkFont(size=12), text_color="#bfdbfe").pack()
        
        # Two columns
        columns = ctk.CTkFrame(main, fg_color="transparent")
        columns.pack(fill="both", expand=True)
        
        # LEFT PANEL
        left = ctk.CTkFrame(columns, corner_radius=12, fg_color="white", width=340)
        left.pack(side="left", fill="both", padx=(0, 10))
        left.pack_propagate(False)
        
        left_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        left_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        left_inner = ctk.CTkFrame(left_scroll, fg_color="transparent")
        left_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Refresh Button
        ctk.CTkLabel(left_inner, text="Controls", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        self.refresh_btn = ctk.CTkButton(left_inner, text="Fetch Latest News", height=40, fg_color="#1e40af", command=self.fetch_news)
        self.refresh_btn.pack(fill="x", pady=(0, 10))
        
        # Auto Refresh Toggle
        self.auto_refresh_var = ctk.BooleanVar(value=False)
        auto_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        auto_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkCheckBox(auto_frame, text="Auto Refresh (60 sec)", variable=self.auto_refresh_var, command=self.toggle_auto_refresh).pack(side="left")
        self.auto_refresh_status = ctk.CTkLabel(auto_frame, text="", font=ctk.CTkFont(size=10), text_color="#64748b")
        self.auto_refresh_status.pack(side="left", padx=(10, 0))
        
        # Last update time
        self.last_update_label = ctk.CTkLabel(left_inner, text="Last update: Never", font=ctk.CTkFont(size=11), text_color="#64748b")
        self.last_update_label.pack(anchor="w", pady=(0, 15))
        
        # Category Filter
        ctk.CTkLabel(left_inner, text="Filter by Category", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        self.category_var = ctk.StringVar(value="All")
        for cat in self.categories_display:
            ctk.CTkRadioButton(left_inner, text=cat, variable=self.category_var, value=cat, command=self.filter_by_category).pack(anchor="w", pady=3)
        
        # Separator
        ctk.CTkFrame(left_inner, height=1, fg_color="#e2e8f0").pack(fill="x", pady=15)
        
        # Source Filter
        ctk.CTkLabel(left_inner, text="Filter by Source", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        sources = ["All"] + list(self.rss_feeds.keys())
        if self.api_key != "YOUR_API_KEY_HERE":
            sources.insert(1, "NewsAPI")
        
        self.source_var = ctk.StringVar(value="All")
        self.source_menu = ctk.CTkComboBox(left_inner, values=sources, variable=self.source_var, command=self.filter_by_source)
        self.source_menu.pack(fill="x", pady=(0, 15))
        
        # Search Section
        ctk.CTkLabel(left_inner, text="Search News", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(left_inner, placeholder_text="Enter keyword...", height=38)
        self.search_entry.pack(fill="x", pady=(0, 10))
        
        self.search_btn = ctk.CTkButton(left_inner, text="Search", height=35, fg_color="#4f46e5", command=self.search_news)
        self.search_btn.pack(fill="x", pady=(0, 5))
        
        self.reset_btn = ctk.CTkButton(left_inner, text="Reset Filters", height=35, fg_color="#64748b", command=self.reset_filters)
        self.reset_btn.pack(fill="x", pady=(0, 15))
        
        # Save Section
        ctk.CTkLabel(left_inner, text="Save News", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        self.save_btn = ctk.CTkButton(left_inner, text="Save Current News", height=40, fg_color="#10b981", command=self.save_news)
        self.save_btn.pack(fill="x", pady=(0, 10))
        
        self.view_saved_btn = ctk.CTkButton(left_inner, text="View Saved News", height=40, fg_color="#4f46e5", command=self.view_saved_news)
        self.view_saved_btn.pack(fill="x", pady=(0, 5))
        
        # Status
        self.status_label = ctk.CTkLabel(left_inner, text="Ready", font=ctk.CTkFont(size=11), text_color="#64748b")
        self.status_label.pack(anchor="w", pady=(15, 0))
        
        # RIGHT PANEL
        right = ctk.CTkFrame(columns, corner_radius=12, fg_color="white")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Tab view
        tab_view = ctk.CTkTabview(right, corner_radius=12)
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # News Tab
        news_tab = tab_view.add(" News")
        self.setup_news_tab(news_tab)
        
        # Trending Tab
        trending_tab = tab_view.add(" Trending")
        self.setup_trending_tab(trending_tab)
        
        # Saved Tab
        saved_tab = tab_view.add(" Saved")
        self.setup_saved_tab(saved_tab)
    
    def setup_news_tab(self, parent):
        # Treeview frame
        tree_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree_inner = ctk.CTkFrame(tree_frame, fg_color="transparent")
        tree_inner.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.tree = ttk.Treeview(tree_inner, show="headings", height=16)
        self.tree.pack(fill="both", expand=True)
        
        vsb = ttk.Scrollbar(tree_inner, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(tree_inner, orient="horizontal", command=self.tree.xview)
        hsb.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Columns with Description
        columns = ["#", "Title", "Source", "Category", "Date", "Description"]
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Title":
                self.tree.column(col, width=300)
            elif col == "Description":
                self.tree.column(col, width=400)
            elif col == "Source":
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=80)
        self.tree.column("#", width=40)
        
        self.tree.bind("<Double-1>", self.open_news_url)
    
    def setup_trending_tab(self, parent):
        # Trending section
        trending_frame = ctk.CTkFrame(parent, fg_color="#fef2f2", border_width=1, border_color="#fecaca", corner_radius=8)
        trending_frame.pack(fill="x", padx=10, pady=10)
        
        trending_inner = ctk.CTkFrame(trending_frame, fg_color="transparent")
        trending_inner.pack(padx=15, pady=12)
        
        ctk.CTkLabel(trending_inner, text=" TRENDING NEWS (Most Shared/Viewed)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#dc2626").pack(anchor="w")
        
        # Treeview for trending
        tree_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree_inner = ctk.CTkFrame(tree_frame, fg_color="transparent")
        tree_inner.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.trending_tree = ttk.Treeview(tree_inner, show="headings", height=15)
        self.trending_tree.pack(fill="both", expand=True)
        
        vsb = ttk.Scrollbar(tree_inner, orient="vertical", command=self.trending_tree.yview)
        vsb.pack(side="right", fill="y")
        self.trending_tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(tree_inner, orient="horizontal", command=self.trending_tree.xview)
        hsb.pack(side="bottom", fill="x")
        self.trending_tree.configure(xscrollcommand=hsb.set)
        
        columns = ["#", "Title", "Source", "Category", "Shares"]
        self.trending_tree["columns"] = columns
        for col in columns:
            self.trending_tree.heading(col, text=col)
            if col == "Title":
                self.trending_tree.column(col, width=500)
            else:
                self.trending_tree.column(col, width=100)
        self.trending_tree.column("#", width=40)
        
        self.trending_tree.bind("<Double-1>", self.open_trending_url)
    
    def setup_saved_tab(self, parent):
        tree_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tree_inner = ctk.CTkFrame(tree_frame, fg_color="transparent")
        tree_inner.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.saved_tree = ttk.Treeview(tree_inner, show="headings", height=15, selectmode="extended")
        self.saved_tree.pack(fill="both", expand=True)
        
        vsb = ttk.Scrollbar(tree_inner, orient="vertical", command=self.saved_tree.yview)
        vsb.pack(side="right", fill="y")
        self.saved_tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(tree_inner, orient="horizontal", command=self.saved_tree.xview)
        hsb.pack(side="bottom", fill="x")
        self.saved_tree.configure(xscrollcommand=hsb.set)
        
        columns = ["#", "Title", "Source", "Category", "Saved Date"]
        self.saved_tree["columns"] = columns
        for col in columns:
            self.saved_tree.heading(col, text=col)
            if col == "Title":
                self.saved_tree.column(col, width=500)
            else:
                self.saved_tree.column(col, width=120)
        self.saved_tree.column("#", width=40)
        
        self.saved_tree.bind("<Double-1>", self.open_saved_url)
        
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="Delete Selected", height=35, fg_color="#ef4444", command=self.delete_selected_saved).pack(side="left", padx=(0, 10), fill="x", expand=True)
        ctk.CTkButton(btn_frame, text="Delete All", height=35, fg_color="#dc2626", command=self.delete_all_saved).pack(side="left", fill="x", expand=True)
    
    def categorize_article(self, title, description):
        text = (title + " " + description).lower()
        for category, keywords in self.categories.items():
            if category == "General":
                continue
            for keyword in keywords:
                if keyword in text:
                    return category
        return "General"
    
    def calculate_trending_score(self, title, description, source):
        """Calculate trending score based on keywords and source popularity"""
        score = 0
        text = (title + " " + description).lower()
        
        # Trending keywords
        trending_keywords = ["breaking", "update", "new", "launch", "announce", "reveal", 
                             "exclusive", "first", "major", "important", "urgent", "alert"]
        
        for keyword in trending_keywords:
            if keyword in text:
                score += 2
        
        # Source popularity boost
        popular_sources = ["BBC News", "CNN", "TechCrunch"]
        if source in popular_sources:
            score += 3
        
        # Title length boost (longer titles might be more detailed)
        if len(title) > 80:
            score += 1
        
        return min(score, 20)  # Max 20
    
    def detect_trending_news(self):
        """Detect trending news based on scores"""
        trending = []
        for article in self.news_data:
            score = self.calculate_trending_score(
                article.get('title', ''), 
                article.get('description', ''), 
                article.get('source', '')
            )
            if score >= 5:  # Only high-scoring news
                trending.append({
                    'title': article['title'],
                    'source': article['source'],
                    'category': article.get('category', 'General'),
                    'url': article['url'],
                    'score': score
                })
        
        # Sort by score (highest first)
        trending.sort(key=lambda x: x['score'], reverse=True)
        self.trending_news = trending[:20]  # Top 20 trending
        
        # Update trending display
        self.display_trending_news()
    
    def display_trending_news(self):
        for item in self.trending_tree.get_children():
            self.trending_tree.delete(item)
        
        for i, article in enumerate(self.trending_news, 1):
            self.trending_tree.insert("", "end", values=(
                i,
                article['title'][:100],
                article['source'],
                article['category'],
                f" {article['score']}"
            ))
        
        self.status_label.configure(text=f" {len(self.trending_news)} trending news detected")
    
    def fetch_news_api(self, category):
        if self.api_key == "20b99313efe341c795c4f6c059bdce11":
            return []
        
        try:
            category_code = "general"
            if category == "Technology":
                category_code = "technology"
            elif category == "Business":
                category_code = "business"
            elif category == "Sports":
                category_code = "sports"
            elif category == "Entertainment":
                category_code = "entertainment"
            
            url = f"https://newsapi.org/v2/top-headlines?country=us&category={category_code}&apiKey={self.api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("status") == "ok":
                articles = []
                for article in data.get("articles", [])[:15]:
                    if article.get("title") and article.get("title") != "[Removed]":
                        articles.append({
                            'title': article['title'][:200],
                            'description': article.get('description', 'No description available')[:400],
                            'source': "NewsAPI",
                            'url': article.get('url', '#'),
                            'date': article.get('publishedAt', '').split('T')[0],
                            'category': category
                        })
                return articles
            return []
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []
    
    def fetch_rss_feed(self, source_name, feed_data):
        try:
            feed = feedparser.parse(feed_data["url"])
            articles = []
            for entry in feed.entries[:15]:
                category = self.categorize_article(entry.get('title', ''), entry.get('description', ''))
                
                # Get description
                description = entry.get('description', '')
                if not description:
                    description = entry.get('summary', 'No description available')
                description = description[:400]
                
                articles.append({
                    'title': entry.get('title', 'No title')[:200],
                    'description': description,
                    'source': source_name,
                    'url': entry.get('link', '#'),
                    'date': entry.get('published', '').split(' ')[0],
                    'category': category
                })
            return articles
        except Exception as e:
            print(f"RSS error for {source_name}: {e}")
            return []
    
    def toggle_auto_refresh(self):
        if self.auto_refresh_var.get():
            self.auto_refresh = True
            self.auto_refresh_status.configure(text=" ON", text_color="#10b981")
            self.start_auto_refresh()
        else:
            self.auto_refresh = False
            self.auto_refresh_status.configure(text=" OFF", text_color="#64748b")
    
    def start_auto_refresh(self):
        def auto_refresh_loop():
            while self.auto_refresh:
                time.sleep(self.refresh_interval)
                if self.auto_refresh:
                    self.root.after(0, self.fetch_news)
        
        thread = threading.Thread(target=auto_refresh_loop, daemon=True)
        thread.start()
    
    def fetch_news(self):
        self.refresh_btn.configure(state="disabled", text="Fetching...")
        self.status_label.configure(text="Fetching news from all sources...")
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        def fetch_all():
            all_news = []
            
            if self.api_key != "YOUR_API_KEY_HERE":
                for category in ["General", "Technology", "Business", "Sports", "Entertainment"]:
                    news = self.fetch_news_api(category)
                    all_news.extend(news)
                    self.root.after(0, self.update_status, f"Fetched {category} from NewsAPI")
            
            for source_name, feed_data in self.rss_feeds.items():
                news = self.fetch_rss_feed(source_name, feed_data)
                all_news.extend(news)
                self.root.after(0, self.update_status, f"Fetched from {source_name}")
            
            self.news_data = all_news
            self.filtered_data = all_news
            
            # Detect trending news
            self.detect_trending_news()
            
            self.root.after(0, self.display_news)
            self.root.after(0, self.fetch_complete)
        
        threading.Thread(target=fetch_all).start()
    
    def update_status(self, message):
        self.status_label.configure(text=message)
    
    def display_news(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        display_data = data if data is not None else self.filtered_data
        
        for i, article in enumerate(display_data, 1):
            self.tree.insert("", "end", values=(
                i,
                article['title'][:100],
                article['source'],
                article.get('category', 'General'),
                article.get('date', 'N/A'),
                article.get('description', 'No description')[:100]
            ))
        
        self.last_update_label.configure(text=f"Last update: {datetime.now().strftime('%H:%M:%S')}")
        self.status_label.configure(text=f" Showing {len(display_data)} news articles")
    
    def fetch_complete(self):
        self.refresh_btn.configure(state="normal", text="Fetch Latest News")
        self.status_label.configure(text=f" Fetched {len(self.news_data)} news articles")
    
    def filter_by_category(self):
        selected_category = self.category_var.get()
        
        if selected_category == "Trending":
            self.display_trending_news()
            self.status_label.configure(text=f" Showing {len(self.trending_news)} trending news")
            return
        elif selected_category == "All":
            self.filtered_data = self.news_data
        else:
            self.filtered_data = [n for n in self.news_data if n.get('category') == selected_category]
        
        self.display_news()
        self.status_label.configure(text=f" Showing {len(self.filtered_data)} news in '{selected_category}' category")
    
    def filter_by_source(self, source):
        if source == "All":
            self.filtered_data = self.news_data
        else:
            self.filtered_data = [n for n in self.news_data if n['source'] == source]
        
        self.display_news()
        self.status_label.configure(text=f" Showing {len(self.filtered_data)} news from '{source}'")
    
    def search_news(self):
        keyword = self.search_entry.get().strip().lower()
        if not keyword:
            messagebox.showwarning("Warning", "Please enter a keyword")
            return
        
        filtered = []
        for article in self.news_data:
            if keyword in article['title'].lower() or keyword in article.get('description', '').lower():
                filtered.append(article)
        
        if filtered:
            self.filtered_data = filtered
            self.display_news()
            self.status_label.configure(text=f" Found {len(filtered)} news matching '{keyword}'")
        else:
            messagebox.showinfo("Not Found", f"No news found matching '{keyword}'")
    
    def reset_filters(self):
        self.category_var.set("All")
        self.source_var.set("All")
        self.search_entry.delete(0, "end")
        self.filtered_data = self.news_data
        self.display_news()
        self.status_label.configure(text=f" Reset filters. Showing all {len(self.news_data)} news")
    
    def save_news(self):
        if not self.filtered_data:
            messagebox.showwarning("Warning", "No news to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")],
            initialfile=f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            save_data = []
            for article in self.filtered_data:
                save_article = article.copy()
                save_article['saved_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                save_data.append(save_article)
                self.saved_news.append(save_article)
            
            if filename.endswith('.csv'):
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Title", "Source", "Category", "Date", "Description", "URL"])
                    for article in save_data:
                        writer.writerow([
                            article['title'],
                            article['source'],
                            article.get('category', 'General'),
                            article.get('date', 'N/A'),
                            article.get('description', ''),
                            article['url']
                        ])
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.save_saved_news()
            messagebox.showinfo("Success", f"Saved {len(save_data)} news to {filename}")
    
    def load_saved_news(self):
        if os.path.exists(self.saved_file):
            try:
                with open(self.saved_file, 'r', encoding='utf-8') as f:
                    self.saved_news = json.load(f)
            except:
                self.saved_news = []
        else:
            self.saved_news = []
    
    def save_saved_news(self):
        with open(self.saved_file, 'w', encoding='utf-8') as f:
            json.dump(self.saved_news, f, indent=2, ensure_ascii=False)
    
    def view_saved_news(self):
        for item in self.saved_tree.get_children():
            self.saved_tree.delete(item)
        
        for i, article in enumerate(self.saved_news, 1):
            self.saved_tree.insert("", "end", values=(
                i,
                article['title'][:100],
                article['source'],
                article.get('category', 'General'),
                article.get('saved_date', 'N/A')
            ))
        
        self.status_label.configure(text=f" Showing {len(self.saved_news)} saved news articles")
    
    def delete_selected_saved(self):
        selected = self.saved_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select news to delete (Ctrl+Click for multiple)")
            return
        
        if not messagebox.askyesno("Confirm", f"Delete {len(selected)} selected news items?"):
            return
        
        indices = []
        for item in selected:
            value = self.saved_tree.item(item, 'values')[0]
            indices.append(int(value) - 1)
        
        indices.sort(reverse=True)
        
        for idx in indices:
            if 0 <= idx < len(self.saved_news):
                self.saved_news.pop(idx)
        
        self.save_saved_news()
        self.view_saved_news()
        messagebox.showinfo("Success", f"Deleted {len(selected)} news items")
    
    def delete_all_saved(self):
        if not self.saved_news:
            messagebox.showwarning("Warning", "No saved news to delete")
            return
        
        if messagebox.askyesno("Confirm", f"Delete ALL {len(self.saved_news)} saved news? This cannot be undone!"):
            self.saved_news = []
            self.save_saved_news()
            self.view_saved_news()
            messagebox.showinfo("Success", "All saved news deleted")
    
    def open_news_url(self, event):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item, 'values')
            idx = int(values[0]) - 1
            if 0 <= idx < len(self.filtered_data):
                webbrowser.open(self.filtered_data[idx].get('url', '#'))
    
    def open_saved_url(self, event):
        selected = self.saved_tree.selection()
        if selected:
            item = selected[0]
            values = self.saved_tree.item(item, 'values')
            idx = int(values[0]) - 1
            if 0 <= idx < len(self.saved_news):
                webbrowser.open(self.saved_news[idx].get('url', '#'))
    
    def open_trending_url(self, event):
        selected = self.trending_tree.selection()
        if selected:
            item = selected[0]
            values = self.trending_tree.item(item, 'values')
            idx = int(values[0]) - 1
            if 0 <= idx < len(self.trending_news):
                webbrowser.open(self.trending_news[idx].get('url', '#'))

if __name__ == "__main__":
    app = NewsAggregator()
