# 🎥 Telegram Video Compressor Bot  
**Powered by FFmpeg (H.265 / H.264) + Flask + Render**

This Telegram bot compresses videos using **FFmpeg (libx265 / libx264)** and returns a smaller output while maintaining visual quality.  
Resolution, codec, CRF, audio, and subtitle settings are customizable directly inside Telegram through `/settings`.

---

## ✨ Key Features

| Feature | Description |
|--------|-------------|
| H.265 / H.264 compression | Toggle codec directly through `/settings` |
| Resolution change | 480p / 720p / 1080p |
| CRF value control | Adjust compression / quality |
| Audio support | Keep or remove audio |
| Subtitle support | Keep subtitles (auto MKV output when copying subs) |
| Always online | Flask server keeps Render container alive |
| No VPS required | Fully cloud based (Render deployment) |

> Output size can reduce **70–90%** depending on source video.

---

## 🧠 How to Use

| Step | Action |
|------|--------|
| 1️⃣ | Send `/start` to bot |
| 2️⃣ | Use `/settings` to adjust compression options |
| 3️⃣ | **Send video as Document** (important) |
| 4️⃣ | Bot compresses the video |
| 5️⃣ | Bot sends compressed output back |

---

## 📸 Screenshots

Put your images inside:

assets/
├── settings_menu.png
├── compression_result.png
└── render_logs.png

yaml
Copy code

Example usage:

<img src="assets/settings_menu.png" width="420px">
<img src="assets/compression_result.png" width="420px">
<img src="assets/render_logs.png" width="420px">

---

## 🗂 Project Structure

.
├── bot.py # Telegram bot logic
├── ffmpeg_utils.py # FFmpeg command builder
├── settings_store.py # Saves user preferences (JSON)
├── app.py # Flask keep-alive server for Render
├── run.py # Runs both bot + Flask
├── Dockerfile # FFmpeg + Python environment setup
├── requirements.txt # Dependency list
└── render.yaml # Render deployment config

yaml
Copy code

---

## 🔧 Deployment (Render.com)

### 1️⃣ Clone / Fork Repository

```bash
git clone https://github.com/Liveserver01/Video-Compress
cd Video-Compress
2️⃣ Create bot via BotFather
bash
Copy code
/newbot
Copy the generated BOT_TOKEN.

3️⃣ Deploy on Render
Go to https://render.com

New → Web Service

Select this GitHub repository

Render auto-detects Dockerfile

Add environment variable:

Key	Value
BOT_TOKEN	Your BotFather bot token

✅ Deploy — bot starts automatically.

🧪 Bot Commands
Command	Description
/start	Initialize bot
/settings	Configure compression options
/help	Display usage guide

🔗 Social Links
<table> <tr> <td><a href="https://t.me/TechnicalHackGuide"><img src="https://img.shields.io/badge/Telegram-Join_Channel-blue?logo=telegram&style=for-the-badge"></a></td> <td><a href="https://instagram.com/virendra_chauhan_1"><img src="https://img.shields.io/badge/Instagram-Follow-purple?logo=instagram&style=for-the-badge"></a></td> <td><a href="https://youtube.com/@Technical-hack-guide"><img src="https://img.shields.io/badge/YouTube-Subscribe-red?logo=youtube&style=for-the-badge"></a></td> </tr> </table>
GitHub Repository → https://github.com/Liveserver01/Video-Compress

⭐ Support
If this bot helped you, consider giving the repo a ⭐

mathematica
Copy code
https://github.com/Liveserver01/Video-Compress
