# Telegram Video Compressor Bot (FFmpeg + Flask + Render)

A production-ready Telegram bot that compresses videos using FFmpeg. Defaults to **H.265/HEVC (libx265)** with these presets:

- Resolution choices: **480p, 720p, 1080p**
- Framerate: **same as source**
- Encode preset: **medium** (and optional **low** → uses `slow` internally)
- Encode profile: **main10**
- Encode level: **4.0**
- CRF: **24**
- Audio: **same as source** or **skip**
- Subtitles: **same as source** or **skip**

Bot also supports **H.264/AVC (libx264)** if you switch codec from settings.

It runs a **Flask** health server alongside the bot so the service stays live on Render.

## Project Structure

.
├── bot.py # Telegram bot (python-telegram-bot v20, asyncio)
├── ffmpeg_utils.py # FFmpeg command builder and helpers
├── settings_store.py # Per-user settings (JSON file)
├── app.py # Flask keepalive app (/health)
├── run.py # Starts Flask + bot polling together
├── requirements.txt # Python deps
├── Dockerfile # Ensures FFmpeg exists on Render
├── render.yaml # Render deployment config
├── Procfile # For local Procfile runners (optional)
└── README.md # How to run/deploy
