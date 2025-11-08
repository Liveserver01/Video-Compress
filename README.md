# 🎥 Telegram Video Compressor Bot (FFmpeg + Flask + Render)

A powerful Telegram bot that compresses videos using **FFmpeg (H.265 / H.264)** with multiple options such as:
- Resolution change (480p / 720p / 1080p)
- H.265 (HEVC) / H.264 (AVC) codec toggle
- CRF selection for quality control
- Audio keep / skip
- Subtitles keep / skip (auto switches to MKV if subs are kept)
- Runs 24×7 using Flask on Render.com

> ✅ Output video size reduces up to **70–90%** while maintaining quality.

---

## 🚀 Live Demo / Bot Link

👉 (Add your bot link here when publicly available)

---

## 🔧 Features

| Feature | Description |
|--------|-------------|
| 🎯 Compression | H.265 / H.264 FFmpeg compression |
| 📉 Resolution Change | Choose 480p / 720p / 1080p |
| 🔁 Codec Switch | Switch codec LIVE from `/settings` |
| 🔊 Audio Options | Keep audio / Remove audio |
| 💬 Subtitles | Keep subtitles / remove (auto MKV output when keeping subs) |
| ⚙️ CRF Control | Lower CRF = better quality, higher CRF = more compression |
| 🌍 Always Live | Runs continuously using Flask on Render |

---

## 📁 Project Structure
.
├── bot.py # Telegram bot logic
├── ffmpeg_utils.py # FFmpeg command builder
├── settings_store.py # Stores per-user compression preferences
├── app.py # Flask keep-alive server for Render
├── run.py # Runs both bot + Flask simultaneously
├── Dockerfile # Ensures FFmpeg is installed on Render
├── requirements.txt # Required Python packages
└── render.yaml # Render deployment config


---

## 🛠️ How to Use Bot (User Guide)

| Step | Action |
|------|--------|
| ✅ Step 1 | Send `/start` in bot chat |
| ⚙️ Step 2 | Type `/settings` to customize options |
| 🎥 Step 3 | Send **video as Document** (not as video) |
| ⏳ Step 4 | Bot compresses using FFmpeg |
| 📥 Step 5 | Bot returns compressed output video |

---

## 🧠 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Starts the bot |
| `/settings` | Show compression options |
| `/help` | Usage guide |

---

## 🖥️ Deploy on Render (No VPS Required)

### 1️⃣ Fork/Clone Repo

👉 GitHub Repo:  
🔗 **https://github.com/Liveserver01/Video-Compress**

```bash
git clone https://github.com/Liveserver01/Video-Compress
cd Video-Compress

2️⃣ Create bot on Telegram (BotFather)

/newbot
Get BOT_TOKEN

3️⃣ Deploy to Render

Login → https://render.com

Create New → Web Service

Select GitHub repo

Render automatically detects Dockerfile

Add environment variable:

| Key         | Value          |
| ----------- | -------------- |
| `BOT_TOKEN` | Your bot token |

✅ Deploy — bot runs automatically.

📍 Important Notes

Always send video as Document, otherwise Telegram compresses it on its own.

For max quality, use:

Codec: H.265

Resolution: 720p

CRF: 24

Preset: medium

🔗 Social Links
<table> <tr> <td><a href="https://t.me/TechnicalHackGuide"><img src="https://img.shields.io/badge/Telegram-Join%20Channel-blue?logo=telegram&style=for-the-badge"/></a></td> <td><a href="https://instagram.com/virendra_chauhan_1"><img src="https://img.shields.io/badge/Instagram-Follow%20Now-orange?logo=instagram&style=for-the-badge"/></a></td> <td><a href="https://youtube.com/@Technical-hack-guide"><img src="https://img.shields.io/badge/YouTube-Subscribe-red?logo=youtube&style=for-the-badge"/></a></td> </tr> </table>

🧑‍💻 Author

Virendra Chauhan

Telegram: https://t.me/TechnicalHackGuide

Instagram: https://instagram.com/virendra_chauhan_1

YouTube: https://youtube.com/@Technical-hack-guide

⭐ Support

If this helps you, star the repo — it motivates further development.

👉 https://github.com/Liveserver01/Video-Compress


# 🎥 Telegram Video Compressor Bot (FFmpeg + Flask + Render)

A powerful Telegram bot that compresses videos using **FFmpeg (H.265 / H.264)** with multiple options such as:
- Resolution change (480p / 720p / 1080p)
- CRF quality control
- Audio keep / remove
- Subtitles keep / remove (auto MKV)
- Always live 24×7 (powered by Flask on Render)

> ✅ Reduces size up to **70–90%** while maintaining quality.

---

## 🚀 Demo Bot Link
> (Add your bot link here once you make it public)

---

## 🖼️ Screenshots / Preview

> Upload screenshots to your repo in a new folder `/assets/`  
> Then update the image links below.

