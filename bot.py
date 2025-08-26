import os
import logging
import asyncio
import subprocess
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

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
    keyboard = [
        [InlineKeyboardButton("📹 Video Compress", callback_data="compress")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
        [InlineKeyboardButton("⭐ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Namaste! Main Video Compress Bot hoon.\n\n"
        "🎥 Mujhe koi video bhejo, main usse compress karke dunga.\n"
        "👇 Niche se ek option select karo:",
        reply_markup=reply_markup
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "compress":
        await query.edit_message_text("📩 Mujhe apna video bhejo, main usse compress karunga.")
    elif query.data == "help":
        await query.edit_message_text("❓ Help:\nBas mujhe video bhejo aur main usse compress karke dunga.")
    elif query.data == "about":
        await query.edit_message_text("ℹ️ About:\nYe bot Flask + python-telegram-bot + FFmpeg se banaya gaya hai.")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("📥 Video download ho raha hai...")

    # Step 1: video download
    file = await context.bot.get_file(update.message.video.file_id)
    input_path = f"input_{update.message.video.file_id}.mp4"
    output_path = f"compressed_{update.message.video.file_id}.mp4"
    await file.download_to_drive(input_path)

    await msg.edit_text("⚙️ Video compress ho raha hai...")

    # Step 2: compress using FFmpeg
    try:
        command = [
            "ffmpeg", "-i", input_path,
            "-vcodec", "libx264", "-crf", "28",  # CRF 28 = decent compression
            "-preset", "fast",
            "-acodec", "aac",
            output_path
        ]
        subprocess.run(command, check=True)

        await msg.edit_text("📤 Compressed video bheja ja raha hai...")

        # Step 3: send compressed video
        await update.message.reply_video(video=open(output_path, "rb"))

    except Exception as e:
        await msg.edit_text(f"❌ Compression failed: {e}")
        logger.error(f"FFmpeg Error: {e}")
    finally:
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❗ Sirf video bhejo ya /start command use karo.")

# ==============================
# Handlers Registration
# ==============================
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# ==============================
# Flask webhook route
# ==============================
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
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

    async def set_webhook():
        await application.bot.delete_webhook()
        await application.bot.set_webhook(
            url=f"{RENDER_URL}/webhook/{BOT_TOKEN}",
            allowed_updates=["message", "callback_query"]
        )
        print("✅ Webhook set:", f"{RENDER_URL}/webhook/{BOT_TOKEN}")

    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
