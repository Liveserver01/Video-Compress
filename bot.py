import os
import tempfile
import subprocess
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 5000))
RENDER_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is running on Render!"


# ============== TELEGRAM BOT ==============
user_settings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎥 Compress Video", callback_data="compress")]]
    await update.message.reply_text(
        "👋 Namaste! Main aapka Video Compression Bot hu.\n"
        "Mujhe video bhejiye ya neeche button par click kijiye.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "compress":
        user_settings[query.from_user.id] = {
            "codec": "libx265",
            "resolution": "720p",
            "preset": "medium",
            "crf": 24,
            "audio": "copy",
            "subs": "copy",
        }
        await query.edit_message_text("⚙️ Default compression settings set! Ab mujhe apna video bhejiye 📩")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_settings:
        await update.message.reply_text("⚠️ Pehle /start kijiye.")
        return

    file = await context.bot.get_file(update.message.video.file_id)
    input_path = tempfile.mktemp(suffix=".mp4")
    output_path = tempfile.mktemp(suffix=".mp4")
    await file.download_to_drive(input_path)

    settings = user_settings[user_id]
    resolution = "1280x720"  # default 720p

    ffmpeg_cmd = [
        "ffmpeg", "-i", input_path,
        "-c:v", settings["codec"], "-preset", settings["preset"],
        "-crf", str(settings["crf"]),
        "-vf", f"scale={resolution}",
        "-c:a", settings["audio"], "-c:s", settings["subs"],
        output_path,
    ]

    try:
        await update.message.reply_text("⏳ Compressing video...")
        subprocess.run(ffmpeg_cmd, check=True)
        await update.message.reply_video(video=open(output_path, "rb"), caption="✅ Done!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        for f in [input_path, output_path]:
            try: os.remove(f)
            except: pass


# ============== TELEGRAM APPLICATION ==============
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"


if __name__ == "__main__":
    import asyncio

    async def init():
        # Purana webhook hatao aur naya lagao
        await application.bot.delete_webhook()
        await application.bot.set_webhook(f"{RENDER_URL}/webhook/{BOT_TOKEN}")
        print("✅ Webhook set:", f"{RENDER_URL}/webhook/{BOT_TOKEN}")

    asyncio.get_event_loop().run_until_complete(init())
    app.run(host="0.0.0.0", port=PORT)
