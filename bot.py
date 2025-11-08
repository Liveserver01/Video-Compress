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
    "crf": 24,                # integer
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
