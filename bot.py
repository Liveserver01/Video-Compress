# Telegram Video Compressor Bot (FFmpeg + Flask + Render)

A production‑ready Telegram bot that compresses videos using FFmpeg. Defaults to **H.265/HEVC (libx265)** with these presets:

* Resolution choices: **480p, 720p, 1080p**
* Framerate: **same as source**
* Encode preset: **medium** (and optional **low** → uses `slow` internally)
* Encode profile: **main10** (HEVC)
* Encode level: **4.0**
* CRF: **24** (adjustable)
* Audio: **same as source** or **skip**
* Subtitles: **same as source** or **skip** (if copying subs, output container switches to `.mkv` to avoid mp4 limitations)

Bot also supports **H.264/AVC (libx264)** if you switch codec from settings.

It runs a **Flask** health server alongside the bot so the service stays live on Render.

---

## Project Structure

```
.
├── bot.py                 # Telegram bot (python-telegram-bot v20, asyncio)
├── ffmpeg_utils.py        # FFmpeg command builder and helpers
├── settings_store.py      # Per-user settings (JSON file)
├── app.py                 # Flask keepalive app (/health)
├── run.py                 # Starts Flask + bot polling together
├── requirements.txt       # Python deps
├── Dockerfile             # Ensures FFmpeg exists on Render
├── render.yaml            # Render deployment config
├── Procfile               # For local Procfile runners (optional)
└── README.md              # How to run/deploy
```

---

## bot.py

```python
import asyncio
import logging
import os
import tempfile
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

from ffmpeg_utils import build_ffmpeg_cmd, guess_container, human_size
from settings_store import SettingsStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("compress-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var is required")

# Defaults per requirement
DEFAULT_SETTINGS = {
    "codec": "h265",          # h265 (libx265) or h264 (libx264)
    "resolution": "720p",     # 480p / 720p / 1080p
    "preset": "medium",       # medium / low (mapped to x265 'slow')
    "crf": 24,                 # integer
    "audio": "copy",          # copy / none
    "subs": "none"            # copy / none
}

store = SettingsStore("settings.json", DEFAULT_SETTINGS)

# --- UI Helpers ---

def settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    s = store.get(user_id)
    row1 = [
        InlineKeyboardButton(f"Codec: {s['codec'].upper()}", callback_data="noop"),
        InlineKeyboardButton("Toggle", callback_data="toggle_codec")
    ]
    row2 = [
        InlineKeyboardButton(f"Res: {s['resolution']}", callback_data="noop"),
        InlineKeyboardButton("480p", callback_data="set_res_480p"),
        InlineKeyboardButton("720p", callback_data="set_res_720p"),
        InlineKeyboardButton("1080p", callback_data="set_res_1080p"),
    ]
    row3 = [
        InlineKeyboardButton(f"Preset: {s['preset']}", callback_data="noop"),
        InlineKeyboardButton("medium", callback_data="set_preset_medium"),
        InlineKeyboardButton("low", callback_data="set_preset_low"),
    ]
    row4 = [
        InlineKeyboardButton(f"CRF: {s['crf']}", callback_data="noop"),
        InlineKeyboardButton("-", callback_data="crf_minus"),
        InlineKeyboardButton("+", callback_data="crf_plus"),
    ]
    row5 = [
        InlineKeyboardButton(f"Audio: {s['audio']}", callback_data="noop"),
        InlineKeyboardButton("same", callback_data="set_audio_copy"),
        InlineKeyboardButton("skip", callback_data="set_audio_none"),
    ]
    row6 = [
        InlineKeyboardButton(f"Subs: {s['subs']}", callback_data="noop"),
        InlineKeyboardButton("same", callback_data="set_subs_copy"),
        InlineKeyboardButton("skip", callback_data="set_subs_none"),
    ]
    return InlineKeyboardMarkup([row1, row2, row3, row4, row5, row6])

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        "Namaste! Video bhejo (video ya document). /settings se options badal sakte ho.\n\n"
        "Defaults: H.265 main10 L4.0, CRF 24, preset medium, framerate same, audio copy, subs skip, res 720p."
    )

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("Current settings:", reply_markup=settings_keyboard(user_id))

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    s = store.get(user_id)

    if data == "toggle_codec":
        s["codec"] = "h264" if s["codec"] == "h265" else "h265"
    elif data.startswith("set_res_"):
        s["resolution"] = data.split("_")[-1]
    elif data.startswith("set_preset_"):
        s["preset"] = data.split("_")[-1]
    elif data == "crf_minus":
        s["crf"] = max(0, int(s["crf"]) - 1)
    elif data == "crf_plus":
        s["crf"] = min(51, int(s["crf"]) + 1)
    elif data == "set_audio_copy":
        s["audio"] = "copy"
    elif data == "set_audio_none":
        s["audio"] = "none"
    elif data == "set_subs_copy":
        s["subs"] = "copy"
    elif data == "set_subs_none":
        s["subs"] = "none"

    store.set(user_id, s)
    await query.edit_message_reply_markup(reply_markup=settings_keyboard(user_id))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/settings – options change karo\n"
        "Video bhejo as file (document) for best quality."
    )

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id
    s = store.get(user_id)

    file_obj = None
    file_name = None

    if message.document and message.document.mime_type and message.document.mime_type.startswith("video/"):
        file_obj = await message.document.get_file()
        file_name = message.document.file_name or "input.mp4"
    elif message.video:
        file_obj = await message.video.get_file()
        file_name = "input.mp4"
    else:
        await message.reply_text("Please send a video (document preferred).")
        return

    status = await message.reply_text("Downloading…")

    try:
        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / file_name
            out_ext = guess_container(s["codec"], s["subs"])  # mp4 or mkv
            out_path = Path(td) / f"out.{out_ext}"

            await file_obj.download_to_drive(custom_path=str(in_path))
            await status.edit_text("Compressing with FFmpeg… (this can take a while)")

            cmd = build_ffmpeg_cmd(
                input_file=str(in_path),
                output_file=str(out_path),
                codec=s["codec"],
                resolution=s["resolution"],
                preset=s["preset"],
                crf=int(s["crf"]),
                audio=s["audio"],
                subs=s["subs"],
            )

            logger.info("FFmpeg: %s", " ".join(cmd))

            # run ffmpeg in a thread to avoid blocking event loop
            proc_rc = await asyncio.to_thread(run_ffmpeg, cmd)
            if proc_rc != 0 or not out_path.exists():
                raise RuntimeError("FFmpeg failed")

            size = out_path.stat().st_size
            await status.edit_text(f"Uploading… ({human_size(size)})")

            await message.reply_document(
                document=str(out_path),
                caption=(
                    f"Codec: {s['codec']} | {s['resolution']} | CRF {s['crf']} | "
                    f"preset {s['preset']} | audio {s['audio']} | subs {s['subs']}"
                )
            )
            await status.delete()
    except Exception as e:
        logger.exception("Compression error")
        await status.edit_text(f"Error: {e}")


def run_ffmpeg(cmd):
    import subprocess
    return subprocess.call(cmd)


async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("settings", show_settings))
    app.add_handler(CallbackQueryHandler(on_button))

    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_media))

    await app.initialize()
    await app.start()
    logger.info("Bot started (polling)")
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ffmpeg_utils.py

```python
from pathlib import Path

# Map UI preset to encoder preset
# "low" in UI → slower encode (better quality). We'll map to 'slow'.
PRESET_MAP = {
    "medium": "medium",
    "low": "slow",
}

RES_MAP = {
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
}

def guess_container(codec: str, subs: str) -> str:
    # If subs are copied, mp4 often fails. Use mkv instead.
    if subs == "copy":
        return "mkv"
    return "mp4"


def build_ffmpeg_cmd(
    *, input_file: str, output_file: str, codec: str, resolution: str,
    preset: str, crf: int, audio: str, subs: str
):
    h = RES_MAP.get(resolution, 720)

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file,
        # Keep FPS same as source: do not set -r
        "-vf", f"scale=-2:{h}",
    ]

    if codec == "h265":
        cmd += [
            "-c:v", "libx265",
            "-preset", PRESET_MAP.get(preset, "medium"),
            "-crf", str(crf),
            "-x265-params", "profile=main10:level=4.0",
        ]
    else:
        # h264 fallback
        cmd += [
            "-c:v", "libx264",
            "-preset", PRESET_MAP.get(preset, "medium"),
            "-crf", str(crf),
            "-profile:v", "high",
            "-level:v", "4.0",
        ]

    # Audio handling
    if audio == "copy":
        cmd += ["-c:a", "copy"]
    else:
        cmd += ["-an"]  # no audio

    # Subtitles handling
    if subs == "copy":
        cmd += ["-c:s", "copy"]
    else:
        cmd += ["-sn"]  # drop subs

    cmd += [output_file]
    return cmd


def human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} TB"
```

---

## settings_store.py

```python
import json
import threading
from pathlib import Path

class SettingsStore:
    def __init__(self, path: str, defaults: dict):
        self.path = Path(path)
        self.defaults = defaults
        self._lock = threading.Lock()
        if not self.path.exists():
            self._write({})

    def _read(self):
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text("utf-8"))
        except Exception:
            return {}

    def _write(self, data: dict):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
        tmp.replace(self.path)

    def get(self, user_id: int) -> dict:
        with self._lock:
            data = self._read()
            s = data.get(str(user_id), {}).copy()
            out = self.defaults.copy()
            out.update(s)
            return out

    def set(self, user_id: int, settings: dict):
        with self._lock:
            data = self._read()
            data[str(user_id)] = settings
            self._write(data)
```

---

## app.py (Flask keepalive)

```python
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def root():
    return "OK", 200

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
```

---

## run.py (start Flask + Bot together)

```python
import asyncio
import threading
import os
from app import app as flask_app
from bot import main as bot_main

# Run Flask server in a thread

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    asyncio.run(bot_main())
```

---

## requirements.txt

```
python-telegram-bot==20.7
Flask==3.0.3
```

> FFmpeg is provided via Dockerfile below; no extra Python packages required.

---

## Dockerfile

```dockerfile
FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy deps first for better cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Env
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Start the service (web service expected by Render)
CMD ["python", "run.py"]
```

---

## render.yaml (Render deployment)

```yaml
services:
  - type: web
    name: telegram-video-compressor
    env: docker
    plan: free
    autoDeploy: true
    envVars:
      - key: BOT_TOKEN
        sync: false  # set in Render dashboard
```

---

## Procfile (optional for local Procfile runners/Heroku-style)

```
web: python run.py
```

---

## README.md

### 1) Local Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export BOT_TOKEN=123456:ABC-DEF  # PowerShell: $env:BOT_TOKEN="..."
python run.py
```

Send `/start` to your bot and upload a test video.

### 2) GitHub Upload

* Create a new repository and push all files.

### 3) Deploy on Render (Docker)

1. In Render, **New > Web Service > Build from repo** and select your GitHub repo.
2. Render reads `Dockerfile`. No build command needed.
3. Set environment variable: `BOT_TOKEN` with your BotFather token.
4. Deploy. A web URL will be visible; it serves `/health` and runs the bot polling in parallel.

> **Note:** We use long polling (stable, no webhook SSL hassles). Flask just keeps the web service responsive.

### 4) Usage

* `/settings` → inline menu to change: codec (H.265/H.264), resolution, CRF, preset, audio, subs.
* Send video as **document** to avoid Telegram auto-recompression.
* Defaults match your spec: **H.265 main10 L4.0, CRF 24, preset medium, FPS same as source, audio copy, subs skip, res 720p.**

### 5) Notes & Tips

* **Preset "low"** in UI maps to encoder preset **slow** (higher quality, slower speed). You can change mapping in `ffmpeg_utils.py`.
* If you choose **Subs: same as source**, output container becomes **.mkv** to preserve subtitles safely.
* Temporary files are processed in `/tmp` and deleted after each job.
* If you want webhooks later, you can add a webhook route to Flask and switch `python-telegram-bot` to `webhook` mode.

### 6) Troubleshooting

* If uploads fail, your output file may exceed Telegram file size limits (2GB for many accounts). Try 480p or higher CRF.
* Some old devices can’t play H.265. Switch codec to H.264 from settings.
* Audio copy may fail for exotic codecs/containers. If you see an error, set **Audio: skip**.

```
```
