# Bot Auto Tweet Trending V2 - Dokumentasi

Selamat datang di Bot Auto Tweet V2, sebuah solusi otomatisasi Twitter yang canggih dan fleksibel. Proyek ini dirancang untuk bekerja 24/7 secara mandiri menggunakan GitHub Actions untuk meningkatkan visibilitas dan interaksi akun Anda.

Proyek ini terbagi menjadi **tiga bot utama** yang dapat dijalankan secara independen:
1.  **`bot_v1.1.py`**: Bot orisinal dengan kemampuan parsing file `.txt` yang kompleks (mendukung format multi-baris dengan `text:`, `media:`, `hashtags:`).
2.  **`bot_rss.py`**: Bot cerdas yang memantau RSS feed dan secara otomatis memposting artikel baru, lengkap dengan gambar.
3.  **`bot_txt.py`**: Bot sederhana yang memposting konten secara acak dari file `.txt` dengan format "satu baris satu tweet".
4.  **`bot_tweet_image.py`**: Bot cerdas yang memposting konten secara acak dari file `.txt` di tambah dengan gambar dari file `.txt`.
5.  **`scrape_action.py`**: Bot Cerdas yang bisa mengambil url/link gambar dari Pixabay dan google untuk di jadikan konten Tweet.
6.  **`bot_autonews.py`**: Bot Cerdas yang mengambil data trends dari twitter/x dan di olah menggunakan AI sehingga menjadi konten tweet Berita dan sangat potensi menjadikan Konten tweet kita viral.

---

## Keunggulan & Fitur

* **Otomatisasi Penuh 24/7**: Atur sekali dan biarkan bot bekerja selamanya, memposting konten sesuai jadwal yang Anda tentukan di GitHub Actions.
* **Jangkauan Organik Maksimal**: Secara cerdas mengambil topik dan hashtag yang sedang tren di Indonesia (Bisa di Ubah Target Negara) dari sumber eksternal untuk ditambahkan ke setiap tweet.
* **Sumber Konten Tak Terbatas**:
    * **RSS Feed**: Tarik berita atau artikel terbaru secara otomatis dari situs berita atau situs/blog Anda (Feed Suport XML).
    * **File Teks**: Siapkan ratusan konten tweet di dalam file `.txt` untuk diposting secara acak atau terjadwal.
* **Manajemen Konten Cerdas**:
    * Bot RSS mengingat artikel yang sudah diposting dan akan memproses antrean artikel baru satu per satu, mencegah postingan duplikat.
    * Mendukung format multi-baris yang kompleks, memberikan Anda kendali penuh atas tampilan tweet, termasuk baris baru dan spasi.
* **Konfigurasi Eksternal Fleksibel**: Atur jumlah tren yang diinginkan dan bahkan ubah target trending negara melalui file `.txt` sederhana tanpa perlu mengubah kode Python.
* **Dilindungi Sistem Lisensi**: Bot ini memerlukan lisensi untuk dapat berjalan, memastikan penggunaannya tetap terkontrol dan eksklusif.

---

## Panduan Setup

### Struktur File Penting
Pastikan file-file berikut ada di dalam repositori Anda untuk fungsionalitas penuh:
* **Skrip Bot**: `bot_v1.1.py`, `bot_rss.py`, `bot_txt.py`,`bot_autonews.py`,`bot_tweet_image.py`.
* **File Jadwal**: Di dalam `.github/workflows/`, terdapat `v1.1_workflow.yml`, `rss_workflow.yml`, `txt_workflow.yml`,`autonews_workflow.yml`.
* **File Data & Konfigurasi**:
    * `tweets_media.txt`, `config/v1.1_config.json` (Set Up Untuk Bot Auto Tweet Trending V1.1)
    * `tweet.txt`, `config/bottext_config.json` (Set Up Untuk Bot Auto Tweet - Txt File)
    * `posted_rss_links.txt`, `config/botrss_config.json` (Set Up Untuk Bot Auto Tweet - RSS Feed)
    * `image_list.txt`, `tweets_image.txt`, `config/botimage_config.json` (Set Up Untuk Bot Tweet + Gambar)
    * `config/autonews_config.json` (Set Up Untuk Auto Tweet News AI)
   

### Pengaturan GitHub Secrets
Bot ini memerlukan kunci (secrets) untuk dapat berfungsi. Buka repositori Anda, lalu pergi ke **Settings > Secrets and variables > Actions**.

Anda perlu menambahkan *secrets* berikut:

* **Kunci Twitter API**:
    * `TWITTER_API_KEY`
    * `TWITTER_API_SECRET`
    * `TWITTER_ACCESS_TOKEN`
    * `TWITTER_ACCESS_TOKEN_SECRET`
* **Kunci Lisensi Bot**:
    * `BOT_LICENSE_EMAIL`: Lisensi berupa email ketika pembelian di: [Beli Lisensi Hanya Rp 265.000](https://lynk.id/belajaradmobpemula/62e39l28yd2o)

* **Kunci API**:
   * `PIXABAY_API_KEY`
   * `GEMINI_API_KEY`
 
## Kebijakan Lisensi

Lisensi yang Anda beli bersifat personal dan terikat pada email pembelian Anda.

* **Pemakaian Tak Terbatas (Unlimited)**: Satu lisensi dapat digunakan untuk mengotomatisasi akun Twitter dalam jumlah tidak terbatas, selama semua bot dijalankan dari dalam repositori GitHub yang sama milik pemegang lisensi.
* **Larangan Berbagi atau Menjual Kembali**: Lisensi ini tidak dapat dipindahtangankan, dibagikan, atau dijual kembali kepada pihak lain dalam bentuk apapun.
* **Hak Pengembang**: Pengembang memiliki hak penuh untuk menonaktifkan (ban) lisensi secara permanen dan tanpa pengembalian dana jika terdeteksi adanya pelanggaran, seperti upaya berbagi atau menjual kembali lisensi.

---

Twitter Demo: [Drakorku](https://x.com/Drakorku99)

---
---

# Bot Auto Tweet Trending V2 (English Version)

Welcome to Auto Tweet Trending Bot V2, a sophisticated, flexible, and secure Twitter automation solution. This project is designed to run 24/7 autonomously using GitHub Actions to increase your account's visibility and engagement.

This project is divided into **three main, independent bots**:
1.  **`bot_v1.1.py`**: The original bot with a complex `.txt` file parser (supporting multi-line formats with `text:`, `media:`, `hashtags:`).
2.  **`bot_rss.py`**: An intelligent bot that monitors an RSS feed and automatically posts new articles, complete with images.
3.  **`bot_txt.py`**: A simple bot that posts random content from a text file using a "one line, one tweet" format.
4.  **`bot_tweet_image.py`**: An intelligent bot that posts random content from a .txt file, paired with an image from a separate .txt file.
5.  **`scrape_action.py`**: An intelligent bot that can scrape image URLs/links from both Pixabay and Google to be used as tweet content.
6.  **`bot_autonews.py`**: An intelligent bot that takes trending data from Twitter/X and processes it using AI to create news tweet content with high potential to go viral.

---

## Advantages & Features

* **24/7 Full Automation**: Set it up once and let the bot work forever, posting content according to the schedule you define in GitHub Actions.
* **Maximum Organic Reach**: Intelligently scrapes trending topics and hashtags from Indonesia (Target Country is Changeable) from an external source to be added to each tweet.
* **Unlimited Content Sources**:
    * **RSS Feed**: Automatically pull the latest news or articles from your favorite news sites or your own site/blog (Supports XML Feed).
    * **Text File**: Prepare hundreds of tweet contents inside `.txt` files to be posted randomly or on a schedule.
* **Intelligent Content Management**:
    * The RSS bot remembers which articles have been posted and will process a queue of new articles one by one, preventing duplicate posts.
    * Supports complex multi-line formats, giving you full control over the tweet's appearance, including newlines and spacing.
* **Flexible External Configuration**: Set the desired number of trends and even change the target country for trends through simple `.txt` files without needing to change the Python code.
* **License-Protected**: This bot requires a license to run, ensuring its usage remains controlled and exclusive.

---

## Setup Guide

### Important File Structure
Ensure the following files are present in your repository for full functionality:
* **Bot Scripts**: `bot_v1.1.py`, `bot_rss.py`, `bot_txt.py`,`bot_autonews.py`,`bot_tweet_image.py`.
* **Workflow Files**: Inside `.github/workflows/`, you should have `v1.1_workflow.yml`, `rss_workflow.yml`, `txt_workflow.yml`, `autonews_workflow.yml`.
* **Data & Config Files**:
    * `tweets_media.txt`, `config/v1.1_config.json` (Set Up For Bot Auto Tweet Trending V1.1)
    * `tweet.txt`, `config/bottext_config.json` (Set Up For Bot Auto Tweet - Txt File)
    * `posted_rss_links.txt`, `config/botrss_config.json` (Set Up For Bot Auto Tweet - RSS Feed)
    * `image_list.txt`, `tweets_image.txt`, `config/botimage_config.json` (Set Up For Bot Tweet + Gambar)
    * `config/autonews_config.json` (Set Up For Auto Tweet News AI)

### GitHub Secrets Setup
This bot requires secrets to function. Go to your repository's **Settings > Secrets and variables > Actions**.

You need to add the following secrets:
* **Bot License Key**:
    * `BOT_LICENSE_EMAIL`: License in the form of an email upon purchase at: [Buy License $17](https://lynk.id/belajaradmobpemula/62e39l28yd2o)
* **Twitter API Keys**:
    * `TWITTER_API_KEY`
    * `TWITTER_API_SECRET`
    * `TWITTER_ACCESS_TOKEN`
    * `TWITTER_ACCESS_TOKEN_SECRET`
 
* **API Key**:
   * `PIXABAY_API_KEY`
   * `GEMINI_API_KEY`
 
## License Policy

The license you purchase is personal and is bound to your purchase email.

* **Unlimited Use**: A single license can be used to automate an unlimited number of Twitter accounts, as long as all bots are run from within the same GitHub repository belonging to the license holder.
* **No Sharing or Reselling**: This license is non-transferable and may not be shared with or resold to any other party in any form.
* **Developer's Rights**: The developer reserves the full right to permanently deactivate (ban) a license without a refund if any violation is detected, such as attempts to share or resell the license.


---

Twitter Demo: [Drakorku](https://x.com/Drakorku99)
