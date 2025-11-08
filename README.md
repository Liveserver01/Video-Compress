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

<img src="assets/settings_menu.png" width="420px">
<img src="assets/compression_result.png" width="420px">
<img src="assets/render_logs.png" width="420px">

---

## 🗂 Project Structure

.
├── bot.py # Telegram bot logic
├── ffmpeg_utils.py # FFmpeg command builder
├── settings_store.py # Saves user preferences (JSON)
├── app.py # Flask keep-alive server
├── run.py # Runs bot + Flask
├── Dockerfile # FFmpeg + Python environment
├── requirements.txt # Dependencies
└── render.yaml # Render deployment config


---

## 🛠️ Deployment (Render)

### 1️⃣ Clone Repo

```bash
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

🧪 Commands
Command	Description
/start	Start bot
/settings	Configure compression
/help	Usage guide

<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>

## 🚀 Features  

- 📥 **Instant Movie Save**  
  Forward movies or posters from your channel and auto-save to `movie_list.json` & GitHub repository.  

- 🛠 **Secure Admin Panel**  
  Password-protected admin interface to manage your movie list without touching the code.  

- 📌 **Bulk Add & Bulk Delete**  
  Add or remove multiple movies in one go, with an easy “Add More” button.  

- 🔄 **GitHub Sync**  
  Real-time update of movie list to your GitHub repo for permanent storage.  

- 📤 **Bulk Send with Delay**  
  Send or forward multiple movies with a built-in delay to avoid Telegram spam limits.  

- 🖼 **Movie Poster with Search Result**  
  अब जब भी आप मूवी का नाम लिखते हैं, बॉट मूवी का पोस्टर और नाम दोनों भेजता है 📸🎬  

- ⚙ **Custom Settings**  
  Change bot behavior (auto-forward ON/OFF, delay time, etc.) directly from the panel.  

- 📝 **Activity Logs**  
  All admin actions are recorded in `bot.log` for transparency and troubleshooting.

<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>

## 📂 File Structure  

📁 project-root
├── app.py # Flask Admin Panel & API
├── bot.py # Telegram Bot main script
├── updater.py # GitHub sync functions
├── settings.json # Bot settings
├── movie_list.json # Saved movie data
├── bot.log # Action logs
└── requirements.txt # Dependencies


<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>

## ⚙ Environment Variables  

| Variable Name         | Description |
|-----------------------|-------------|
| `BOT_TOKEN`           | Your Telegram Bot API Token |
| `ADMIN_PASSWORD`      | Admin Panel password |
| `CHANNEL_ID`          | Your Telegram channel ID |
| `CHANNEL_INVITE`      | Permanent invite link of your channel |
| `FLASK_SECRET_KEY`    | Flask session secret key |
| `GITHUB_TOKEN`        | GitHub personal access token |
| `GITHUB_REPO`         | GitHub repo name (e.g. `username/repo`) |
| `GITHUB_FILE_PATH`    | Path to `movie_list.json` in repo |
| `GITHUB_BRANCH`       | Branch name (default: `main`) |
| `OMDB_API_KEY`        | OMDB API KEY |

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


## 📜 License  

MIT License © 2025 VIRENDRA CHAUHAN 
<a href="https://github.com/Liveserver01/Telegram_chat_bot" target="_blank">
  <img src="https://img.shields.io/badge/Bot%20Creator-VIRENDRA%20CHAUHAN-4CAF50?style=for-the-badge" alt="Bot: created by VIRENDRA CHAUHAN"/>
</a>

💡 *Easily manage, share, and store your movie collection without hassle!*  
