=============================

README (महत्वपूर्ण निर्देश)

=============================


=============================

main.py (पूरा production-ready बॉट)

=============================

import asyncio import json import logging import os import shutil import tempfile import uuid from dataclasses import dataclass, asdict from typing import Dict, Optional, Tuple

from dotenv import load_dotenv from telegram import ( Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile, ) from telegram.constants import ChatAction from telegram.ext import ( Application, ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, )

load_dotenv()

--------- Logging ---------

logging.basicConfig( format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO, ) logger = logging.getLogger(name)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") if not BOT_TOKEN: raise RuntimeError("TELEGRAM_BOT_TOKEN missing. Set it in environment variables or .env file.")

Concurrency limit (avoid RAM/CPU overload)

MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1")) job_semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

---------------- Settings Model ----------------

@dataclass class EncodeSettings: codec: str = "libx265"  # libx265 (H.265) or libx264 (H.264) resolution: str = "source"  # source|480p|720p|1080p preset: str = "medium"  # medium|low (low == slow) crf: int = 24 audio: str = "copy"  # copy|skip subs: str = "copy"  # copy|skip profile: str = "main10"  # HEVC main10 (only for x265) level: str = "4.0"

def preset_value(self) -> str:
    if self.preset == "low":
        return "slow"  # user friendly label 'low' -> x264/x265 preset 'slow'
    return "medium"

Per-chat settings in-memory

USER_SETTINGS: Dict[int, EncodeSettings] = {}

-------------- UI Helpers --------------

def settings_keyboard(s: EncodeSettings) -> InlineKeyboardMarkup: codec_btn = [ InlineKeyboardButton( text=("Codec: H.265 (libx265)" if s.codec == "libx265" else "Codec: H.264 (libx264)"), callback_data="toggle_codec", ) ] res_btn = [ InlineKeyboardButton( text=f"Resolution: {s.resolution}", callback_data="cycle_res" ) ] preset_btn = [ InlineKeyboardButton( text=f"Preset: {s.preset}", callback_data="toggle_preset" ) ] audio_btn = [ InlineKeyboardButton( text=f"Audio: {s.audio}", callback_data="toggle_audio" ) ] subs_btn = [ InlineKeyboardButton( text=f"Subtitles: {s.subs}", callback_data="toggle_subs" ) ] actions = [ InlineKeyboardButton(text="✅ Done", callback_data="close_settings"), InlineKeyboardButton(text="♻️ Reset", callback_data="reset_settings"), ] return InlineKeyboardMarkup([codec_btn, res_btn, preset_btn, audio_btn, subs_btn, actions])

def confirm_keyboard() -> InlineKeyboardMarkup: return InlineKeyboardMarkup( [ [InlineKeyboardButton(text="🎬 Compress", callback_data="do_compress")], [InlineKeyboardButton(text="⚙️ Change Settings", callback_data="open_settings")], [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_job")], ] )

-------------- FFprobe helpers --------------

async def run_cmd(cmd: list) -> Tuple[int, str, str]: """Run a subprocess command, return (returncode, stdout, stderr).""" proc = await asyncio.create_subprocess_exec( *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, ) out_b, err_b = await proc.communicate() return proc.returncode, out_b.decode("utf-8", "ignore"), err_b.decode("utf-8", "ignore")

async def ffprobe_streams(input_path: str) -> dict: cmd = [ "ffprobe", "-v", "error", "-show_streams", "-of", "json", input_path, ] code, out, err = await run_cmd(cmd) if code != 0: raise RuntimeError(f"ffprobe failed: {err}") return json.loads(out)

def build_scale_filter(target: str, width: Optional[int], height: Optional[int]) -> Optional[str]: if target == "source" or not width or not height: return None mapping = {"480p": 480, "720p": 720, "1080p": 1080} th = mapping.get(target) if not th: return None # Maintain AR, enforce even dimensions with -2 trick return f"scale=-2:{th}"

async def build_ffmpeg_cmd( input_path: str, output_path: str, s: EncodeSettings, ) -> list: # probe for resolution decisions streams = await ffprobe_streams(input_path) vstream = next((st for st in streams.get("streams", []) if st.get("codec_type") == "video"), None) in_w = int(vstream.get("width")) if vstream and vstream.get("width") else None in_h = int(vstream.get("height")) if vstream and vstream.get("height") else None

vf = build_scale_filter(s.resolution, in_w, in_h)

cmd = ["ffmpeg", "-y", "-i", input_path, "-map", "0"]  # map all by default

# Video codec & params
if s.codec == "libx265":
    cmd += [
        "-c:v",
        "libx265",
        "-pix_fmt",
        "yuv420p10le",
        "-preset",
        s.preset_value(),
        "-crf",
        str(s.crf),
        "-profile:v",
        s.profile,
        "-level:v",
        s.level,
    ]
else:  # libx264
    cmd += [
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        s.preset_value(),
        "-crf",
        str(s.crf),
        "-profile:v",
        "high",
        "-level:v",
        s.level,
    ]

if vf:
    cmd += ["-vf", vf]

# Audio
if s.audio == "copy":
    cmd += ["-c:a", "copy"]
else:
    cmd += ["-an"]  # no audio

# Subtitles
if s.subs == "copy":
    cmd += ["-c:s", "copy"]
else:
    cmd += ["-sn"]

# Container
cmd += [output_path]
return cmd

-------------- Bot Handlers --------------

WELCOME_TEXT = ( "नमस्ते!\n\n" "यह बॉट आपके वीडियो को FFmpeg से compress/transcode कर देता है.\n" "डिफ़ॉल्ट: H.265 (main10, CRF 24, Level 4.0), Preset = medium, Resolution = source.\n\n" "आप /settings से विकल्प बदल सकते हैं — codec, resolution (480p/720p/1080p), preset (medium/low),\n" "audio (copy/skip), subtitles (copy/skip). अब कोई भी वीडियो भेजें।" )

def get_user_settings(chat_id: int) -> EncodeSettings: if chat_id not in USER_SETTINGS: USER_SETTINGS[chat_id] = EncodeSettings() return USER_SETTINGS[chat_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): s = get_user_settings(update.effective_chat.id) await update.message.reply_text(WELCOME_TEXT) await show_settings(update, context, s)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "वीडियो भेजें → ‘Compress’ दबाएँ → बॉट processed वीडियो लौटाएगा.\n" "किसी भी समय /settings से सेटिंग बदलिए." )

async def show_settings(update_or_cb, context: ContextTypes.DEFAULT_TYPE, s: EncodeSettings): text = ( "⚙️ आपकी वर्तमान सेटिंग्स:\n" f"• Codec: {'H.265 (libx265)' if s.codec=='libx265' else 'H.264 (libx264)'}\n" f"• Resolution: {s.resolution}\n" f"• Preset: {s.preset} (low=slow, medium=balanced)\n" f"• CRF: {s.crf}\n" f"• Profile/Level: {s.profile if s.codec=='libx265' else 'high'}/{s.level}\n" f"• Audio: {s.audio}\n" f"• Subtitles: {s.subs}\n" "\nवीडियो भेजकर ‘Compress’ पर क्लिक करें." ) if isinstance(update_or_cb, Update) and update_or_cb.message: await update_or_cb.message.reply_text(text, reply_markup=settings_keyboard(s)) else: await update_or_cb.edit_message_text(text, reply_markup=settings_keyboard(s))

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): s = get_user_settings(update.effective_chat.id) await show_settings(update, context, s)

async def on_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() chat_id = query.message.chat_id s = get_user_settings(chat_id)

if query.data == "toggle_codec":
    s.codec = "libx264" if s.codec == "libx265" else "libx265"
elif query.data == "cycle_res":
    order = ["source", "480p", "720p", "1080p"]
    s.resolution = order[(order.index(s.resolution) + 1) % len(order)]
elif query.data == "toggle_preset":
    s.preset = "low" if s.preset == "medium" else "medium"
elif query.data == "toggle_audio":
    s.audio = "skip" if s.audio == "copy" else "copy"
elif query.data == "toggle_subs":
    s.subs = "skip" if s.subs == "copy" else "copy"
elif query.data == "reset_settings":
    USER_SETTINGS[chat_id] = EncodeSettings()
    s = USER_SETTINGS[chat_id]
elif query.data == "close_settings":
    await query.edit_message_text("सेटिंग्स सेव हो गईं. अब कोई वीडियो भेजें.")
    return

await show_settings(query, context, s)

Store pending file per chat

PENDING_FILE: Dict[int, Tuple[str, str]] = {}

async def ask_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str, file_name: str): chat_id = update.effective_chat.id PENDING_FILE[chat_id] = (file_id, file_name) await update.message.reply_text( f"मिला: {file_name}\nअब Compress चलाएँ या Settings बदलें:", reply_markup=confirm_keyboard(), )

async def on_video(update: Update, context: ContextTypes.DEFAULT_TYPE): file = None file_name = None

if update.message.video:
    file = update.message.video
    file_name = file.file_name or f"video_{uuid.uuid4().hex}.mp4"
elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("video/"):
    file = update.message.document
    file_name = file.file_name or f"video_{uuid.uuid4().hex}.mkv"

if not file:
    return

await ask_confirm(update, context, file.file_id, file_name)

async def on_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() chat_id = query.message.chat_id

if query.data == "open_settings":
    s = get_user_settings(chat_id)
    await show_settings(query, context, s)
    return
if query.data == "cancel_job":
    PENDING_FILE.pop(chat_id, None)
    await query.edit_message_text("रद्द किया गया.")
    return
if query.data != "do_compress":
    return

pending = PENDING_FILE.get(chat_id)
if not pending:
    await query.edit_message_text("कोई पेंडिंग वीडियो नहीं मिला. कृपया दुबारा भेजें.")
    return

file_id, file_name = pending

# Dispatch the compression task
await query.edit_message_text("🎬 Compression शुरू… कृपया प्रतीक्षा करें.")
try:
    await handle_compress(chat_id, file_id, file_name, context)
    # Clear pending only after success
    PENDING_FILE.pop(chat_id, None)
    await query.edit_message_text("✅ पूरा हुआ! ऊपर processed फ़ाइल देखें.")
except Exception as e:
    logger.exception("Compression failed")
    await query.edit_message_text(f"❌ असफल: {e}")

async def handle_compress(chat_id: int, file_id: str, orig_name: str, context: ContextTypes.DEFAULT_TYPE): s = get_user_settings(chat_id)

async with job_semaphore:
    # Download
    with tempfile.TemporaryDirectory() as td:
        in_path = os.path.join(td, f"in_{uuid.uuid4().hex}")
        # Always mkv output for subtitle compatibility
        base_out = os.path.splitext(os.path.basename(orig_name))[0]
        out_path = os.path.join(td, f"{base_out}_compressed.mkv")

        # Inform typing/upload
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)

        file = await context.bot.get_file(file_id)
        await file.download_to_drive(in_path)

        # Build ffmpeg cmd
        cmd = await build_ffmpeg_cmd(in_path, out_path, s)
        logger.info("FFmpeg: %s", " ".join(cmd))

        # Run ffmpeg
        code, out, err = await run_cmd(cmd)
        if code != 0 or not os.path.exists(out_path):
            raise RuntimeError(f"ffmpeg failed.\nCmd: {' '.join(cmd)}\nError: {err[-1200:]}")

        # Send result back (as document to preserve mkv)
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        caption = (
            f"Codec: {'H.265' if s.codec=='libx265' else 'H.264'} | "
            f"Res: {s.resolution} | Preset: {s.preset} | CRF: {s.crf}\n"
            f"Audio: {s.audio} | Subs: {s.subs}\n"
            f"~{size_mb:.1f} MB"
        )

        # Telegram limits apply; if too big, Telegram may reject — that's expected behavior
        await context.bot.send_document(
            chat_id=chat_id,
            document=InputFile(out_path, filename=os.path.basename(out_path)),
            caption=caption,
        )

-------------- App bootstrap --------------

def build_app() -> Application: app: Application = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("settings", settings_cmd))

app.add_handler(CallbackQueryHandler(on_settings_callback, pattern=r"^(toggle_|cycle_|reset_settings|close_settings)"))
app.add_handler(CallbackQueryHandler(on_confirm_callback, pattern=r"^(do_compress|open_settings|cancel_job)$"))

# Accept both video and video documents
app.add_handler(MessageHandler(filters.VIDEO | (filters.Document.MimeType("video/")), on_video))

return app

if name == "main": app = build_app() logger.info("Starting bot…") app.run_polling(close_loop=False)

=============================

requirements.txt

=============================

python-telegram-bot v20+ (async)

python-telegram-bot==20.7 python-dotenv==1.0.1

=============================

Dockerfile (Render/Any Docker host)

=============================

syntax=docker/dockerfile:1

FROM python:3.11-slim

Install ffmpeg & runtime deps

RUN apt-get update && apt-get install -y --no-install-recommends 
ffmpeg 
ca-certificates 
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app COPY requirements.txt /app/ RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /app/

Env placeholders (override in Render settings)

ENV TELEGRAM_BOT_TOKEN="" ENV MAX_CONCURRENT_JOBS=1

CMD ["python", "main.py"]

=============================

.env.example (लोकल डेवलपमेंट)

=============================

TELEGRAM_BOT_TOKEN=123456:ABC-DEF…

MAX_CONCURRENT_JOBS=1

=============================

render.yaml (optional)

=============================

services:

- type: web

name: tg-video-compressor

env: docker

plan: starter

autoDeploy: true

envVars:

- key: TELEGRAM_BOT_TOKEN

sync: false

- key: MAX_CONCURRENT_JOBS

value: 1

