import asyncio
import json
import logging
import os
import tempfile
import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from dotenv import load_dotenv
from flask import Flask, request
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile,
)
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

load_dotenv()

# --------- Logging ---------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN missing. Set it in environment variables or .env file.")

PORT = int(os.environ.get("PORT", 5000))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
if not RENDER_EXTERNAL_URL:
    raise RuntimeError("RENDER_EXTERNAL_URL missing. Add it in Render dashboard.")

MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))
job_semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)


# ================== Encode Settings ==================
@dataclass
class EncodeSettings:
    codec: str = "libx265"
    resolution: str = "source"  # source|480p|720p|1080p
    preset: str = "medium"      # medium|low
    crf: int = 24
    audio: str = "copy"         # copy|skip
    subs: str = "copy"          # copy|skip
    profile: str = "main10"
    level: str = "4.0"

    def preset_value(self) -> str:
        return "slow" if self.preset == "low" else "medium"


USER_SETTINGS: Dict[int, EncodeSettings] = {}
PENDING_FILE: Dict[int, Tuple[str, str]] = {}


# ================== Keyboards ==================
def settings_keyboard(s: EncodeSettings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=f"Codec: {'H.265' if s.codec=='libx265' else 'H.264'}", callback_data="toggle_codec")],
        [InlineKeyboardButton(text=f"Resolution: {s.resolution}", callback_data="cycle_res")],
        [InlineKeyboardButton(text=f"Preset: {s.preset}", callback_data="toggle_preset")],
        [InlineKeyboardButton(text=f"Audio: {s.audio}", callback_data="toggle_audio")],
        [InlineKeyboardButton(text=f"Subtitles: {s.subs}", callback_data="toggle_subs")],
        [InlineKeyboardButton(text="✅ Done", callback_data="close_settings"),
         InlineKeyboardButton(text="♻️ Reset", callback_data="reset_settings")],
    ])


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🎬 Compress", callback_data="do_compress")],
        [InlineKeyboardButton(text="⚙️ Change Settings", callback_data="open_settings")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_job")],
    ])


# ================== Helpers ==================
async def run_cmd(cmd: list) -> Tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out_b, err_b = await proc.communicate()
    return proc.returncode, out_b.decode("utf-8", "ignore"), err_b.decode("utf-8", "ignore")


async def ffprobe_streams(input_path: str) -> dict:
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-of", "json", input_path]
    code, out, err = await run_cmd(cmd)
    if code != 0:
        raise RuntimeError(f"ffprobe failed: {err}")
    return json.loads(out)


def build_scale_filter(target: str, width: Optional[int], height: Optional[int]) -> Optional[str]:
    if target == "source" or not width or not height:
        return None
    mapping = {"480p": 480, "720p": 720, "1080p": 1080}
    th = mapping.get(target)
    return f"scale=-2:{th}" if th else None


async def build_ffmpeg_cmd(input_path: str, output_path: str, s: EncodeSettings) -> list:
    streams = await ffprobe_streams(input_path)
    vstream = next((st for st in streams.get("streams", []) if st.get("codec_type") == "video"), None)
    in_w = int(vstream.get("width")) if vstream and vstream.get("width") else None
    in_h = int(vstream.get("height")) if vstream and vstream.get("height") else None

    vf = build_scale_filter(s.resolution, in_w, in_h)
    cmd = ["ffmpeg", "-y", "-i", input_path, "-map", "0"]

    if s.codec == "libx265":
        cmd += ["-c:v", "libx265", "-pix_fmt", "yuv420p10le",
                "-preset", s.preset_value(), "-crf", str(s.crf),
                "-profile:v", s.profile, "-level:v", s.level]
    else:
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-preset", s.preset_value(), "-crf", str(s.crf),
                "-profile:v", "high", "-level:v", s.level]

    if vf:
        cmd += ["-vf", vf]
    cmd += ["-c:a", "copy" if s.audio == "copy" else "-an"]
    cmd += ["-c:s", "copy" if s.subs == "copy" else "-sn"]
    cmd += [output_path]
    return cmd


# ================== Bot Handlers ==================
def get_user_settings(chat_id: int) -> EncodeSettings:
    if chat_id not in USER_SETTINGS:
        USER_SETTINGS[chat_id] = EncodeSettings()
    return USER_SETTINGS[chat_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_user_settings(update.effective_chat.id)
    await update.message.reply_text("नमस्ते! 🎬 वीडियो compress करने के लिए भेजें।",
                                    reply_markup=settings_keyboard(s))


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_user_settings(update.effective_chat.id)
    await update.message.reply_text("⚙️ आपकी सेटिंग्स:", reply_markup=settings_keyboard(s))


async def on_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    s = get_user_settings(chat_id)

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
        await query.edit_message_text("✅ सेटिंग्स सेव हो गईं. अब वीडियो भेजें.")
        return

    await query.edit_message_text("⚙️ अपडेटेड सेटिंग्स:", reply_markup=settings_keyboard(s))


async def on_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.video or update.message.document
    if not file:
        return
    PENDING_FILE[update.effective_chat.id] = (file.file_id, file.file_name or f"video_{uuid.uuid4().hex}.mp4")
    await update.message.reply_text("मिला! अब Compress दबाएँ 👇", reply_markup=confirm_keyboard())


async def on_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "open_settings":
        s = get_user_settings(chat_id)
        await query.edit_message_text("⚙️ सेटिंग्स:", reply_markup=settings_keyboard(s))
        return
    if query.data == "cancel_job":
        PENDING_FILE.pop(chat_id, None)
        await query.edit_message_text("❌ रद्द किया गया")
        return
    if query.data != "do_compress":
        return

    if chat_id not in PENDING_FILE:
        await query.edit_message_text("❌ कोई वीडियो नहीं मिला")
        return

    file_id, file_name = PENDING_FILE[chat_id]
    await query.edit_message_text("🎬 Compression शुरू हो रहा है…")
    try:
        await handle_compress(chat_id, file_id, file_name, context)
        PENDING_FILE.pop(chat_id, None)
        await query.edit_message_text("✅ पूरा हुआ! ऊपर फ़ाइल देखें.")
    except Exception as e:
        logger.exception("Compression failed")
        await query.edit_message_text(f"❌ Error: {e}")


async def handle_compress(chat_id: int, file_id: str, orig_name: str, context: ContextTypes.DEFAULT_TYPE):
    s = get_user_settings(chat_id)
    async with job_semaphore:
        with tempfile.TemporaryDirectory() as td:
            in_path = os.path.join(td, "in.mp4")
            base_out = os.path.splitext(os.path.basename(orig_name))[0]
            out_path = os.path.join(td, f"{base_out}_compressed.mkv")

            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)

            file = await context.bot.get_file(file_id)
            await file.download_to_drive(in_path)

            cmd = await build_ffmpeg_cmd(in_path, out_path, s)
            logger.info("Running: %s", " ".join(cmd))
            code, _, err = await run_cmd(cmd)
            if code != 0 or not os.path.exists(out_path):
                raise RuntimeError(f"ffmpeg failed: {err}")

            await context.bot.send_document(
                chat_id=chat_id,
                document=InputFile(out_path, filename=os.path.basename(out_path)),
                caption=f"Codec: {s.codec} | Res: {s.resolution} | CRF: {s.crf}"
            )


# ================== Flask + Webhook ==================
flask_app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("settings", settings_cmd))
application.add_handler(CallbackQueryHandler(on_settings_callback, pattern="^(toggle_|cycle_|reset_|close_)"))
application.add_handler(CallbackQueryHandler(on_confirm_callback, pattern="^(do_compress|open_settings|cancel_job)$"))
application.add_handler(MessageHandler(filters.VIDEO | filters.Document.MimeType("video/"), on_video))


@flask_app.post(f"/{BOT_TOKEN}")
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "ok"


if __name__ == "__main__":
    async def init_bot():
        await application.bot.delete_webhook(drop_pending_updates=True)
        await application.bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}")

    asyncio.run(init_bot())

    # Run with waitress instead of flask.run
    from waitress import serve
    serve(flask_app, host="0.0.0.0", port=PORT)
