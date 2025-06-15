import os
import random
import tweepy
import requests
from bs4 import BeautifulSoup
import sys
import tempfile

# Konfigurasi
TWEETS_FILE = 'tweet.txt'
MAX_TWEET_LENGTH = 250
TRENDING_LIMIT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

class TxtBot:
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
        --- SCRAPER YANG FOKUS ---
        Mengambil tren secara BERURUTAN dari list tren pertama.
        """
        print("🔍 Mengambil tren teratas dari trends24.in (berurutan)...")
        url = "https://www.trends24.in/indonesia/"
        headers = {'User-Agent': USER_AGENT}
        fallback_trends = ['#Indonesia', '#Trending']

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            trends = []

            # Langsung mencari list pertama dengan class 'trend-card__list'
            trend_list_element = soup.find("ol", class_="trend-card__list")

            if not trend_list_element:
                print("⚠️ Tidak menemukan list tren utama. Menggunakan fallback.")
                return fallback_trends

            # Mengambil semua link <a> di dalam list tersebut
            trend_links = trend_list_element.find_all("a")
            
            for link in trend_links:
                trends.append(link.get_text(strip=True))
            
            print(f"✅ Berhasil mendapatkan {len(trends)} item tren.")
            
            # Mengambil dari atas sesuai limit, tanpa diacak.
            return trends[:TRENDING_LIMIT]

        except Exception as e:
            print(f"❌ Gagal scraping: {e}. Menggunakan fallback.")
            return fallback_trends
            
    def parse_tweets_file(self):
        """Membaca file dan menangani format multi-baris."""
        print("📖 Membaca file tweets_media.txt...")
        tweets = []
        try:
            with open(TWEETS_FILE, 'r', encoding='utf-8') as f: content = f.read()
            tweet_blocks = content.strip().split('---')
            for block in tweet_blocks:
                if not block.strip(): continue
                lines = block.strip().split('\n')
                data = {'text': [], 'media': [], 'hashtags': []}
                current_key = None
                for line in lines:
                    parts = line.split(':', 1)
                    if len(parts) == 2 and parts[0].lower() in data:
                        current_key = parts[0].lower()
                        data[current_key].append(parts[1].strip())
                    elif current_key:
                        data[current_key].append(line)
                final_tweet = {}
                if data['text']: final_tweet['text'] = "\n".join(data['text']).strip()
                if data['media']: final_tweet['media'] = [url.strip() for url in "".join(data['media']).split(',')]
                if data['hashtags']: final_tweet['hashtags'] = " ".join(data['hashtags']).split()
                if 'text' in final_tweet: tweets.append(final_tweet)
            if not tweets: raise ValueError("Tidak ada tweet valid")
            return tweets
        except Exception as e:
            print(f"❌ Gagal parsing: {e}"); sys.exit(1)

    def compose_tweet(self, base_text, media_links, default_hashtags):
        """Menyusun tweet dari data .txt."""
        scraped_items = self.get_twitter_trends()
        all_items = scraped_items + default_hashtags
        addon_part = ""
        available_space = MAX_TWEET_LENGTH - len(base_text) - 2
        unique_items = []
        for item in all_items:
            item = item.strip()
            if not item: continue
            if item in default_hashtags and not item.startswith('#'): item = '#' + item
            if item not in unique_items and len(addon_part) + len(item) + 1 <= available_space:
                addon_part += f" {item}"
                unique_items.append(item)
        return f'{base_text}\n\n{addon_part.strip()}', media_links

    def post_tweet(self):
        """Fungsi utama untuk menjalankan bot mode .txt."""
        print("🚀 Memulai bot mode .txt...")
        tweets = self.parse_tweets_file()
        if not tweets: return
        selected_tweet = random.choice(tweets)
        base_text = selected_tweet.get('text', '')
        media_links = selected_tweet.get('media', [])
        hashtags = selected_tweet.get('hashtags', [])
        tweet_text, media_links_for_tweet = self.compose_tweet(base_text, media_links, hashtags)
        media_id = None
        if media_links_for_tweet:
            random_media_url = random.choice(media_links_for_tweet)
            if media_path := self.download_media(random_media_url):
                media_id = self.upload_media(media_path)
        try:
            if media_id: self.client.create_tweet(text=tweet_text, media_ids=[media_id])
            else: self.client.create_tweet(text=tweet_text)
            print("✅ Tweet dari .txt berhasil diposting!")
        except Exception as e:
            print(f"❌ Gagal posting tweet dari .txt: {e}")

    def download_media(self, url):
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(url, headers=headers, stream=True, timeout=15)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '')
            ext = '.jpg';
            if 'png' in content_type: ext = '.png'
            elif 'gif' in content_type: ext = '.gif'
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                for chunk in response.iter_content(chunk_size=8192): tmp_file.write(chunk)
                return tmp_file.name
        except Exception as e:
            print(f"⚠️ Gagal download media: {str(e)}"); return None

    def upload_media(self, media_path):
        if not self.api_v1: return None
        try:
            media = self.api_v1.media_upload(filename=media_path)
            return media.media_id_string
        except Exception as e:
            print(f"⚠️ Gagal upload media: {str(e)}"); return None
        finally:
            try: os.unlink(media_path)
            except: pass

if __name__ == "__main__":
    bot = TxtBot()
    bot.post_tweet()
