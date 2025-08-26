import os
import logging
import subprocess
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# Config
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL", "https://video-compress-jobi.onrender.com")
PORT = int(os.getenv("PORT", 10000))

# ==============================
# Logging
# ==============================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==============================
# Flask app
# ==============================
app = Flask(__name__)

# ==============================
# Telegram Application
# ==============================
application = Application.builder().token(BOT_TOKEN).build()


# ==============================
# Handlers
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Namaste! Main video compress bot hoon.\n\n"
        "🎥 Mujhe koi video bhejo, main usse compress karke dunga."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Commands:\n"
        "/start - Bot shuru karo\n"
        "/help - Madad dekho\n\n"
        "Aur mujhe koi video bhejo, main usse compress kar dunga!"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.video.get_file()
        input_path = "input.mp4"
        output_path = "output.mp4"

        # File download
        await file.download_to_drive(input_path)
        await update.message.reply_text("📥 Video download ho gaya! Ab compress kar raha hoon...")

        # FFmpeg compression
        cmd = [
            "ffmpeg", "-i", input_path,
            "-vcodec", "libx264", "-crf", "28",
            output_path
        ]
        subprocess.run(cmd, check=True)

        # Compressed video bhejna
        await update.message.reply_video(video=open(output_path, "rb"), caption="✅ Yeh lo compressed video!")

        # Clean up
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        logger.error(f"Video process error: {e}")
        await update.message.reply_text("❌ Video process karte waqt error aaya!")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))


# ==============================
# Flask webhook route
# ==============================
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)

        import asyncio
        loop = asyncio.get_event_loop()

        # ✅ Make sure app is initialized & started
        if not application.running:
            loop.run_until_complete(application.initialize())
            loop.run_until_complete(application.start())

        loop.run_until_complete(application.process_update(update))

    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
    return "ok"


@app.route("/")
def home():
    return "🤖 Bot is running!"


# ==============================
# Main
# ==============================
if __name__ == "__main__":
    import asyncio

    async def set_webhook():
        await application.bot.delete_webhook()
        await application.bot.set_webhook(
            url=f"{RENDER_URL}/webhook/{BOT_TOKEN}",
            allowed_updates=["message", "callback_query"]
        )
        print("✅ Webhook set:", f"{RENDER_URL}/webhook/{BOT_TOKEN}")

    asyncio.run(set_webhook())

    # Flask start
    app.run(host="0.0.0.0", port=PORT)
