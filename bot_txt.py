import os
import random
import tweepy
import requests
from bs4 import BeautifulSoup
import sys

# --- KONFIGURASI YANG SUDAH DIPERBAIKI ---
TWEETS_FILE = 'tweet.txt' # DIUBAH: Nama file sesuai permintaan
MAX_TWEET_LENGTH = 250
TRENDING_LIMIT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

class TxtBot:
    def __init__(self):
        # Hanya butuh autentikasi v2 karena bot ini teks-saja
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
        --- ENGINE SCRAPE FINAL ---
        Langsung menargetkan <ol class="trend-card__list"> untuk stabilitas.
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

    def parse_tweets_file(self):
        """
        --- PARSER YANG BENAR UNTUK TWEET PER BARIS ---
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

            # Memasukkan item (hashtag atau frase) apa adanya
            if item not in unique_items and len(addon_part) + len(item) + 1 <= available_space:
                addon_part += f" {item}"
                unique_items.append(item)
        
        return f'{base_text}\n\n{addon_part.strip()}'

    def run(self):
        """Fungsi utama untuk menjalankan bot."""
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
            print(f"❌ Gagal posting tweet: {e}")

if __name__ == "__main__":
    bot = TxtBot()
    bot.run()
