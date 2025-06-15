import os
import random
import tweepy
import requests
from bs4 import BeautifulSoup
import sys

# --- KONFIGURASI UNTUK BOT INI ---
TWEETS_FILE = 'tweet.txt'  # Nama file sesuai permintaan
MAX_TWEET_LENGTH = 250
TRENDING_LIMIT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

class TxtBot:
    def __init__(self):
        self.client = self.authenticate()

    def authenticate(self):
        """Autentikasi dengan Twitter API v2"""
        try:
            return tweepy.Client(
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
        except Exception as e:
            print(f"❌ Gagal autentikasi (v2): {str(e)}")
            sys.exit(1)

    def get_twitter_trends(self):
        """
        --- ENGINE SCRAPE V1.1 (SESUAI PERMINTAAN) ---
        Menggunakan selector asli '.trend-card__list a' yang terbukti bekerja.
        """
        print("🔍 Mengambil tren dari trends24.in (menggunakan selector asli)...")
        url = "https://www.trends24.in/indonesia/"
        headers = {'User-Agent': USER_AGENT}
        fallback_trends = ['#Indonesia', '#Trending']

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            trends = []

            trend_elements = soup.select(".trend-card__list a")
            if not trend_elements:
                print("⚠️ Tidak ada tren yang ditemukan dengan selector ini. Menggunakan fallback.")
                return fallback_trends

            for element in trend_elements:
                text = element.get_text(strip=True)
                if text:
                    trends.append(text)
            
            print(f"✅ Berhasil mendapatkan {len(trends)} item tren mentah.")
            return trends[:TRENDING_LIMIT]
        except Exception as e:
            print(f"❌ Gagal total saat scraping: {e}. Menggunakan fallback.")
            return fallback_trends

    def parse_tweets_file(self):
        """
        --- PARSER SEDERHANA: 1 BARIS = 1 TWEET ---
        Membaca setiap baris dari file sebagai tweet individual.
        """
        print(f"📖 Membaca file {TWEETS_FILE} (mode per baris)...")
        try:
            with open(TWEETS_FILE, 'r', encoding='utf-8') as f:
                # Baca semua baris, hapus spasi berlebih, dan singkirkan baris kosong
                tweets = [line.strip() for line in f if line.strip()]
            
            if not tweets:
                raise ValueError(f"File {TWEETS_FILE} kosong atau tidak ada tweet yang valid.")
            
            print(f"✅ Ditemukan {len(tweets)} konten tweet.")
            return tweets
        except FileNotFoundError:
            print(f"❌ Error: File '{TWEETS_FILE}' tidak ditemukan.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Gagal parsing tweet: {e}")
            sys.exit(1)

    def compose_tweet(self, base_text):
        """
        --- FUNGSI COMPOSE YANG DISEDERHANAKAN ---
        Menggabungkan teks dari file dengan tren hasil scrape.
        """
        scraped_items = self.get_twitter_trends()
        addon_part = ""
        # Sisakan 2 karakter untuk spasi baris baru
        available_space = MAX_TWEET_LENGTH - len(base_text) - 2
        
        unique_items = []
        for item in scraped_items:
            item = item.strip()
            if not item: continue
            if item not in unique_items and len(addon_part) + len(item) + 1 <= available_space:
                addon_part += f" {item}"
                unique_items.append(item)
        
        return f'{base_text}\n\n{addon_part.strip()}'

    def run(self):
        """Fungsi utama untuk menjalankan bot mode .txt."""
        print("🚀 Memulai bot mode .txt (1 baris = 1 tweet)...")
        
        all_tweets = self.parse_tweets_file()
        if not all_tweets:
            return
        
        base_text = random.choice(all_tweets)
        tweet_text = self.compose_tweet(base_text)
        
        try:
            self.client.create_tweet(text=tweet_text)
            print("✅ Tweet berhasil diposting!")
            print(f"   Konten: {tweet_text}")
        except Exception as e:
            print(f"❌ Gagal posting tweet dari .txt: {e}")

if __name__ == "__main__":
    bot = TxtBot()
    bot.run()
