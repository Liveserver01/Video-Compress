🧑‍💻 Author

<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>


# 🎥 Telegram Video Compressor Bot  
**Powered by FFmpeg (H.265 / H.264) + Flask + Render**

This Telegram bot compresses videos using **FFmpeg (libx265 / libx264)** and returns a smaller output while maintaining visual quality.  
Resolution, codec, CRF, audio, and subtitle settings are customizable directly inside Telegram via `/settings`.

---

## ✨ Features

- Compress video using **H.265 / H.264**
- Choose resolution → **480p / 720p / 1080p**
- Adjust **CRF (quality / size balance)**
- Audio → keep or remove
- Subtitle → keep or remove (auto MKV output)
- Runs 24×7 on **Render.com**, no VPS needed
- Sends compressed video back to user

> Output size can reduce **70–90%** depending on video.

---

## 🧠 How to Use

| Step | Action |
|------|--------|
| 1️⃣ | Send `/start` to bot |
| 2️⃣ | Use `/settings` to choose quality options |
| 3️⃣ | **Send video as Document** (important) |
| 4️⃣ | Bot compresses using FFmpeg |
| 5️⃣ | Receive compressed video |

---

## 📸 Screenshots


Example usage:

<img src="assets/start.png" width="420px">
<img src="assets/settings_menu.png" width="420px">
<img src="assets/compression_log.png" width="420px">
<img src="assets/compression_result.png" width="420px">
<img src="assets/render_logs.png" width="420px">

---

## 🛠️ Deployment (Render)

1️⃣ Clone Repo

git clone https://github.com/Liveserver01/Video-Compress
cd Video-Compress

2️⃣ Create bot via BotFather
/newbot
Copy your BOT_TOKEN.

3️⃣ Deploy to Render

Go to https://render.com
Click New → Web Service
Select your GitHub repo
Render auto-detects Dockerfile
Add Environment Variable:
Key	Value
BOT_TOKEN	Your BotFather token
✅ Deploy — bot starts automatically.

⚙ Environment Variables
Variable Name	Description
BOT_TOKEN	Your Telegram Bot API Token


🧪 Commands
Command	Description
/start	Start bot
/settings	Configure compression
/help	Usage guide

<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>

<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>

## 📂 File Structure  
├── bot.py # Telegram bot logic

├── ffmpeg_utils.py # FFmpeg command builder

├── settings_store.py # Saves user preferences (JSON)

├── app.py # Flask keep-alive server

├── run.py # Runs bot + Flask

├── Dockerfile # FFmpeg + Python environment

├── requirements.txt # Dependencies

└── render.yaml # Render deployment config

🔗 Social Links

<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>

<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>
<p align="left">
  <a href="https://facebook.com/virendrachauhan012" target="_blank">
    <img src="https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white" />
  </a>
  <a href="https://youtube.com/@Technical-hack-guide" target="_blank">
    <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  </a>
  <a href="https://t.me/TechnicalHackGuide" target="_blank">
  <img src="https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" />
</a>
  <a href="https://www.threads.net/@virendra_chauhan_1" target="_blank">
    <img src="https://img.shields.io/badge/Threads-000000?style=for-the-badge&logo=threads&logoColor=white" />
  </a>
<a href="https://instagram.com/virendra_chauhan_1" target="_blank">
  <img src="https://img.shields.io/badge/Instagram-%23E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram"/>
</a>
</p>

⭐ Support

If this bot was useful, consider giving the repo a star ⭐

👉 https://github.com/Liveserver01/Video-Compress


## 📜 License  

MIT License © 2025 VIRENDRA CHAUHAN 
<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>
