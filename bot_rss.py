import os
import random
import tweepy
import requests
from bs4 import BeautifulSoup
import sys
import tempfile
import feedparser

# --- KONFIGURASI ---
RSS_CONFIG_FILE = 'rss_config.txt'
POSTED_LINKS_FILE = 'posted_rss_links.txt'
MAX_TWEET_LENGTH = 250
TRENDING_LIMIT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

class RssBot:
    def __init__(self):
        self.client = self.authenticate_v2()
        self.api_v1 = self.authenticate_v1()

    def authenticate_v2(self):
        try:
            return tweepy.Client(
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
        except Exception as e:
            print(f"❌ Gagal autentikasi (v2): {str(e)}"); sys.exit(1)

    def authenticate_v1(self):
        try:
            auth = tweepy.OAuthHandler(os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET'))
            auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
            return tweepy.API(auth)
        except Exception as e:
            print(f"❌ Gagal autentikasi (v1.1): {str(e)}"); return None
    
    def get_twitter_trends(self):
        """
        --- ENGINE SCRAPE FINAL (SESUAI INSTRUKSI SPESIFIK) ---
        Hanya menargetkan <ol class="trend-card__list">.
        """
        print("🔍 Mengambil tren dari trends24.in (target: ol.trend-card__list)...")
        url = "https://www.trends24.in/indonesia/"
        headers = {'User-Agent': USER_AGENT}
        fallback_trends = ['#Indonesia', '#Trending']

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            trends = []

            # LANGSUNG MENCARI ELEMEN <ol> PERTAMA DENGAN CLASS YANG DIMINTA
            trend_list_element = soup.find("ol", class_="trend-card__list")

            if not trend_list_element:
                print("⚠️ Elemen <ol class='trend-card__list'> tidak ditemukan. Menggunakan fallback.")
                return fallback_trends

            # Mengambil semua link <a> di dalam elemen list tersebut
            trend_links = trend_list_element.find_all("a")

            if not trend_links:
                print("⚠️ Elemen <ol> ditemukan, namun tidak ada link tren di dalamnya. Menggunakan fallback.")
                return fallback_trends
            
            for link in trend_links:
                trends.append(link.get_text(strip=True))
            
            print(f"✅ Berhasil mendapatkan {len(trends)} item tren.")
            
            # Mengambil dari atas sesuai limit, tanpa diacak.
            return trends[:TRENDING_LIMIT]

        except Exception as e:
            print(f"❌ Gagal scraping trends24.in: {e}. Menggunakan fallback.")
            return fallback_trends

    def get_new_articles(self):
        try:
            with open(RSS_CONFIG_FILE, 'r') as f: rss_url = f.read().strip()
            if not rss_url: print("❌ File rss_config.txt kosong."); return []
            print(f"📰 Mengambil RSS feed dari: {rss_url}")
            feed = feedparser.parse(rss_url)
            if not os.path.exists(POSTED_LINKS_FILE): open(POSTED_LINKS_FILE, 'w').close()
            with open(POSTED_LINKS_FILE, 'r') as f: posted_links = set(f.read().splitlines())
            new_articles = [entry for entry in feed.entries if entry.link not in posted_links]
            new_articles.reverse()
            return new_articles
        except Exception as e:
            print(f"❌ Gagal memproses RSS feed: {e}"); return []

    def compose_tweet(self, article):
        title = article.title
        link = article.link
        base_text = f"{title}\n\nBaca selengkapnya:\n{link}"
        scraped_trends = self.get_twitter_trends()
        addon_part = ""
        available_space = MAX_TWEET_LENGTH - len(base_text) - 2
        unique_items = []
        for item in scraped_trends:
            item = item.strip()
            if not item: continue
            if item not in unique_items and len(addon_part) + len(item) + 1 <= available_space:
                addon_part += f" {item}"
                unique_items.append(item)
        return f'{base_text}\n\n{addon_part.strip()}'

    def run(self):
        print("🚀 Memulai bot mode RSS...")
        new_articles = self.get_new_articles()
        if not new_articles:
            print("✅ Tidak ada artikel baru untuk diposting.")
            return
        article_to_post = new_articles[0]
        print(f"📬 Menyiapkan untuk memposting artikel: \"{article_to_post.title}\"")
        tweet_text = self.compose_tweet(article_to_post)
        try:
            self.client.create_tweet(text=tweet_text)
            print(f"✅ Tweet artikel berhasil diposting! Link: {article_to_post.link}")
            with open(POSTED_LINKS_FILE, 'a') as f:
                f.write(article_to_post.link + '\n')
        except Exception as e:
            print(f"❌ Gagal memposting tweet artikel: {e}")

if __name__ == "__main__":
    bot = RssBot()
    bot.run()
