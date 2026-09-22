# 🐦 Twitter-X-Downloader-Bot

[English](#english) · [فارسی](#فارسی)

A Telegram bot for downloading **photos, videos, and GIF/video media** from public **X (Twitter)**
posts.

Built with **python-telegram-bot**, **yt-dlp**, **gallery-dl**, and **FFmpeg**.

Author: [iArvin0](https://github.com/iArvin0)

---

# English

## Features

- Download photos from public X/Twitter posts
- Download videos and GIF/video media
- Supports multiple media items in one post
- Supports `x.com`, `twitter.com`, and `t.co`
- `yt-dlp` handles video/GIF media
- `gallery-dl` handles photo media in original/highest available quality
- If yt-dlp returns `No video could be found in this tweet`, the bot still checks for photos
- FFmpeg merges separate video/audio streams when necessary
- Metadata when available: author, duration, views, likes, reposts
- Large photos automatically fall back to Telegram document upload
- Configurable upload size, photo size, concurrency, and timeout
- Optional Netscape-format cookies file for content your own account may access
- Automatic temporary-file cleanup
- Rotating logs
- Bot token redaction in application logs
- Docker / Docker Compose
- GitHub Actions
- Ruff + pytest
- No database
- No forced channel membership

> This bot does not bypass DRM, paywalls, protected/private accounts, or other access controls.

## How it works

```text
X/Twitter URL
     |
     +--> yt-dlp ------> Video / GIF-video
     |
     +--> gallery-dl --> JPG / PNG / WebP / AVIF
     |
     +--> combine media (max 4 by default)
     |
     +--> Telegram
```

Using two extractors is intentional: yt-dlp focuses on playable media while gallery-dl has dedicated
Twitter/X image extraction.

## Supported URLs

```text
https://x.com/username/status/123456789
https://twitter.com/username/status/123456789
https://t.co/AbCdEf12
```

## Requirements

- Python 3.12+
- FFmpeg
- Telegram bot token from BotFather

## Windows

```powershell
git clone https://github.com/iArvin0/Twitter-X-Downloader-Bot.git
cd Twitter-X-Downloader-Bot

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -r requirements.txt
```

Install FFmpeg:

```powershell
winget install -e --id Gyan.FFmpeg
```

Close and reopen PowerShell:

```powershell
ffmpeg -version
ffprobe -version
```

Create `.env`:

```powershell
Copy-Item .env.example .env
```

Set:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

Run:

```powershell
python run.py
```

## Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3 python3-venv ffmpeg

git clone https://github.com/iArvin0/Twitter-X-Downloader-Bot.git
cd Twitter-X-Downloader-Bot

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt

cp .env.example .env
nano .env
python run.py
```

## Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Logs:

```bash
docker compose logs -f
```

Stop:

```bash
docker compose down
```

## Environment variables

| Variable | Default | Description |
|---|---:|---|
| `BOT_TOKEN` | required | Telegram bot token |
| `DOWNLOAD_DIR` | `downloads` | Temporary downloads |
| `LOG_DIR` | `logs` | Log directory |
| `LOG_LEVEL` | `INFO` | Log level |
| `MAX_FILE_SIZE_MB` | `49` | Maximum upload size |
| `MAX_PHOTO_SIZE_MB` | `10` | Above this, images are sent as documents |
| `MAX_CONCURRENT_DOWNLOADS` | `2` | Concurrent downloads |
| `MAX_MEDIA_PER_POST` | `4` | Maximum media from one post |
| `DOWNLOAD_TIMEOUT_SECONDS` | `300` | Extraction/download timeout |
| `YTDLP_COOKIES_FILE` | empty | Optional Netscape cookies file |

## Optional cookies

For content your own account is authorized to view, configure a Netscape-format cookies file:

```env
YTDLP_COOKIES_FILE=C:\path\to\twitter-cookies.txt
```

The same file is passed to both yt-dlp and gallery-dl.

**Never commit cookies to GitHub.** They may expose your account session.

## Commands

```text
/start - Start
/help  - Help
```

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest -q
```

## Project structure

```text
Twitter-X-Downloader-Bot/
├── .github/workflows/ci.yml
├── app/
│   ├── config.py
│   ├── downloader.py
│   ├── errors.py
│   ├── handlers.py
│   ├── image_downloader.py
│   ├── logging_config.py
│   ├── main.py
│   └── utils.py
├── tests/
│   ├── test_errors.py
│   ├── test_image_downloader.py
│   └── test_utils.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── pyproject.toml
├── requirements-dev.txt
├── requirements.txt
├── run.py
└── SECURITY.md
```

## Troubleshooting

### `No video could be found in this tweet`

For an image-only post this is expected from yt-dlp. The bot now continues and asks gallery-dl for
photo media instead of immediately failing.

### Update extractors

```bash
python -m pip install -U "yt-dlp[default]" gallery-dl
```

X/Twitter changes frequently, so keeping extractors current matters.

## License

MIT License — © 2026 iArvin0

---

# فارسی

این پروژه یک بات تلگرام کامل برای دانلود **عکس، ویدئو و GIF/ویدئو** از پست‌های عمومی X/Twitter
است.

بات با `python-telegram-bot`، `yt-dlp`، `gallery-dl` و `FFmpeg` ساخته شده است.

## امکانات

- دانلود عکس از پست‌های X/Twitter
- دانلود ویدئو
- دانلود GIFهایی که X به‌شکل ویدئو ارائه می‌کند
- پشتیبانی از چند رسانه در یک پست
- پشتیبانی از `x.com`
- پشتیبانی از `twitter.com`
- پشتیبانی از `t.co`
- `yt-dlp` برای ویدئو و GIF
- `gallery-dl` برای عکس‌های اصلی
- اگر yt-dlp خطای `No video could be found` بدهد، بات باز هم عکس را بررسی می‌کند
- ادغام ویدئو و صدا با FFmpeg
- ارسال عکس بزرگ به‌صورت Document در صورت نیاز
- محدودیت حجم، تعداد رسانه و دانلود همزمان
- حذف خودکار فایل‌های موقت
- لاگ خطا
- مخفی‌سازی Bot Token در لاگ برنامه
- Docker و Docker Compose
- GitHub Actions
- Ruff و pytest
- بدون SQL
- بدون عضویت اجباری

> این پروژه DRM، paywall، حساب Private/Protected یا سایر محدودیت‌های دسترسی را دور نمی‌زند.

## نصب ویندوز

```powershell
git clone https://github.com/iArvin0/Twitter-X-Downloader-Bot.git
cd Twitter-X-Downloader-Bot

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -r requirements.txt

winget install -e --id Gyan.FFmpeg
```

سپس:

```powershell
Copy-Item .env.example .env
```

داخل `.env`:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

اجرا:

```powershell
python run.py
```

## کوکی اختیاری

اگر حساب خودتان اجازه مشاهده یک پست را دارد، می‌توانید فایل cookies با فرمت Netscape بدهید:

```env
YTDLP_COOKIES_FILE=C:\path\to\twitter-cookies.txt
```

هم `yt-dlp` و هم `gallery-dl` از همان فایل استفاده می‌کنند.

**cookies را هیچ‌وقت روی GitHub قرار ندهید.**

## خطای No video

در نسخه جدید این خطا دیگر شکست فوری نیست؛ بات بعد از آن عکس‌های همان پست را با `gallery-dl`
بررسی می‌کند.

## تست

```bash
python -m pip install -r requirements-dev.txt
python -m ruff check .
python -m pytest -q
```

## لایسنس

MIT License — © 2026 iArvin0
