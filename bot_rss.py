import os
import random
import tweepy
import requests
from bs4 import BeautifulSoup
import sys
import tempfile
import feedparser # Library untuk parsing RSS

# --- KONFIGURASI ---
RSS_CONFIG_FILE = 'rss_config.txt'
LAST_POSTED_LINK_FILE = 'posted_rss_links.txt'
MAX_TWEET_LENGTH = 250
TRENDING_LIMIT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

class RssBot:
    def __init__(self):
        self.client = self.authenticate_v2()
        self.api_v1 = self.authenticate_v1() # Diperlukan untuk upload media

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
        """Mengambil tren dari trends24.in secara berurutan."""
        print("🔍 Mengambil tren teratas dari trends24.in...")
        url = "https://www.trends24.in/indonesia/"
        headers = {'User-Agent': USER_AGENT}
        fallback_trends = ['#Indonesia', '#InfoTerkini']
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            trends = []
            trend_list_element = soup.find("ol", class_="trend-card__list")
            if not trend_list_element: return fallback_trends
            trend_links = trend_list_element.find_all("a")
            if not trend_links: return fallback_trends
            for link in trend_links: trends.append(link.get_text(strip=True))
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

    def get_new_articles(self):
        """Membaca RSS, membandingkan dengan riwayat, dan mengurutkan artikel baru."""
        try:
            with open(RSS_CONFIG_FILE, 'r') as f: rss_url = f.read().strip()
            if not rss_url: print("❌ File rss_config.txt kosong."); return []
            print(f"📰 Mengambil RSS feed dari: {rss_url}")
            feed = feedparser.parse(rss_url)
            benchmark_link = self.read_benchmark_link()
            if not benchmark_link: return []
            
            all_links = [entry.link for entry in feed.entries]
            try:
                benchmark_index = all_links.index(benchmark_link)
                new_articles = feed.entries[:benchmark_index]
                new_articles.reverse()
                return new_articles
            except ValueError:
                print(f"❌ PERINGATAN: Link patokan '{benchmark_link}' tidak ditemukan di feed terbaru. Memulai dari awal.")
                # Jika patokan tidak ada, anggap seperti eksekusi pertama: ambil yang teratas
                return feed.entries[:1]
        except Exception as e:
            print(f"❌ Gagal memproses RSS feed: {e}"); return []
            
    def compose_tweet_text(self, article):
        """Hanya menyusun bagian teks dari tweet."""
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

    def find_image_in_entry(self, entry):
        """Mencari URL gambar di dalam entri RSS."""
        # 1. Cek di 'media_content' (standar media RSS)
        if 'media_content' in entry and entry.media_content:
            for media in entry.media_content:
                if 'url' in media and media.get('medium') == 'image':
                    return media['url']
        # 2. Cek di 'enclosures' (cara lain menyertakan file)
        if 'enclosures' in entry and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'type' in enclosure and 'image' in enclosure.type:
                    return enclosure.href
        # 3. Cek di dalam konten HTML (jika ada)
        if 'summary' in entry:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.has_attr('src'):
                return img_tag['src']
        return None

    def download_media(self, url):
        # ... (fungsi ini sama seperti di bot_txt.py)
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(url, headers=headers, stream=True, timeout=15)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '')
            ext = '.jpg'
            if 'png' in content_type: ext = '.png'
            elif 'gif' in content_type: ext = '.gif'
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                for chunk in response.iter_content(chunk_size=8192): tmp_file.write(chunk)
                return tmp_file.name
        except Exception as e:
            print(f"⚠️ Gagal download media: {str(e)}"); return None

    def upload_media(self, media_path):
        # ... (fungsi ini sama seperti di bot_txt.py)
        if not self.api_v1: return None
        try:
            media = self.api_v1.media_upload(filename=media_path)
            return media.media_id_string
        except Exception as e:
            print(f"⚠️ Gagal upload media: {str(e)}"); return None
        finally:
            try: os.unlink(media_path)
            except: pass

    def run(self):
        """Fungsi utama untuk menjalankan bot mode RSS."""
        print("🚀 Memulai bot mode RSS...")
        new_articles = self.get_new_articles()
        if not new_articles:
            print("✅ Tidak ada artikel baru untuk diposting.")
            return

        article_to_post = new_articles[0]
        print(f"📬 Menyiapkan untuk memposting artikel: \"{article_to_post.title}\"")
        
        tweet_text = self.compose_tweet_text(article_to_post)
        media_id = None
        
        # --- LOGIKA BARU UNTUK GAMBAR ---
        image_url = self.find_image_in_entry(article_to_post)
        if image_url:
            print(f"🖼️ Menemukan gambar: {image_url}")
            media_path = self.download_media(image_url)
            if media_path:
                media_id = self.upload_media(media_path)
                if media_id:
                    print("✅ Gambar berhasil di-upload ke Twitter.")
        else:
            print("ℹ️ Tidak ada gambar yang ditemukan di artikel RSS ini.")
            
        try:
            if media_id:
                self.client.create_tweet(text=tweet_text, media_ids=[media_id])
            else:
                self.client.create_tweet(text=tweet_text)
                
            print(f"✅ Tweet artikel berhasil diposting! Link: {article_to_post.link}")
            self.update_benchmark_link(article_to_post.link)
        except Exception as e:
            print(f"❌ Gagal memposting tweet artikel: {e}")

if __name__ == "__main__":
    bot = RssBot()
    bot.run()
