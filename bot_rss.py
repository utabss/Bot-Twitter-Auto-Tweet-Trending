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
LAST_POSTED_LINK_FILE = 'posted_rss_links.txt' # Nama file diubah untuk kejelasan
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
        --- ENGINE SCRAPE FINAL (SESUAI INSTRUKSI) ---
        Langsung menargetkan <ol class="trend-card__list">.
        """
        print("🔍 Mengambil tren dari trends24.in (target: ol.trend-card__list)...")
        url = "https://www.trends24.in/indonesia/"
        headers = {'User-Agent': USER_AGENT}
        fallback_trends = ['#Indonesia', '#InfoTerkini']

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            trends = []
            trend_list_element = soup.find("ol", class_="trend-card__list")
            if not trend_list_element:
                print("⚠️ Elemen <ol> tidak ditemukan. Menggunakan fallback.")
                return fallback_trends
            trend_links = trend_list_element.find_all("a")
            if not trend_links:
                print("⚠️ Daftar tren kosong. Menggunakan fallback.")
                return fallback_trends
            for link in trend_links:
                trends.append(link.get_text(strip=True))
            print(f"✅ Berhasil mendapatkan {len(trends)} item tren.")
            return trends[:TRENDING_LIMIT]
        except Exception as e:
            print(f"❌ Gagal scraping: {e}. Menggunakan fallback.")
            return fallback_trends

    def read_benchmark_link(self):
        """Membaca satu link patokan dari file."""
        try:
            with open(LAST_POSTED_LINK_FILE, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"❌ File patokan '{LAST_POSTED_LINK_FILE}' tidak ditemukan. Harap buat file ini dan isi dengan satu URL awal.")
            return None

    def update_benchmark_link(self, new_link):
        """Menimpa file patokan dengan link baru."""
        try:
            with open(LAST_POSTED_LINK_FILE, 'w') as f:
                f.write(new_link)
            print(f"✅ File patokan diperbarui dengan link: {new_link}")
        except Exception as e:
            print(f"❌ Gagal memperbarui file patokan: {e}")
            
    def compose_tweet(self, article):
        """Menyusun tweet dari data artikel RSS."""
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
        """Fungsi utama untuk menjalankan bot mode RSS dengan algoritma patokan."""
        print("🚀 Memulai bot mode RSS (algoritma patokan link)...")
        
        # 1. Baca link patokan dari file
        benchmark_link = self.read_benchmark_link()
        if not benchmark_link:
            return

        # 2. Ambil semua artikel dari feed
        try:
            with open(RSS_CONFIG_FILE, 'r') as f: rss_url = f.read().strip()
            if not rss_url: print("❌ File rss_config.txt kosong."); return
            print(f"📰 Mengambil RSS feed dari: {rss_url}")
            feed = feedparser.parse(rss_url)
            all_articles = feed.entries
        except Exception as e:
            print(f"❌ Gagal mengambil atau memproses RSS feed: {e}"); return

        # 3. Cari posisi link patokan di dalam feed
        try:
            all_links = [entry.link for entry in all_articles]
            benchmark_index = all_links.index(benchmark_link)
        except ValueError:
            print(f"❌ PERINGATAN: Link patokan '{benchmark_link}' tidak ditemukan di feed terbaru.")
            print("   Ini bisa terjadi jika bot offline terlalu lama. Harap perbarui link patokan di file secara manual.")
            return

        # 4. Cek apakah sudah update
        if benchmark_index == 0:
            print("✅ Sudah update. Tidak ada artikel baru untuk diposting.")
            return

        # 5. Dapatkan daftar artikel yang lebih baru dari patokan
        new_articles = all_articles[:benchmark_index]
        # Balik urutannya agar yang paling lama (setelah patokan) ada di depan
        new_articles.reverse()

        # 6. Ambil artikel berikutnya untuk diposting
        article_to_post = new_articles[0]
        print(f"📬 Menyiapkan untuk memposting artikel berikutnya: \"{article_to_post.title}\"")
        
        # 7. Susun dan posting tweet
        tweet_text = self.compose_tweet(article_to_post)
        try:
            self.client.create_tweet(text=tweet_text)
            print(f"✅ Tweet artikel berhasil diposting! Link: {article_to_post.link}")
            # 8. Jika berhasil, perbarui file patokan
            self.update_benchmark_link(article_to_post.link)
        except Exception as e:
            print(f"❌ Gagal memposting tweet artikel: {e}")

if __name__ == "__main__":
    bot = RssBot()
    bot.run()
