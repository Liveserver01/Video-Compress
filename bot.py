import os
import logging
import asyncio
import subprocess
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
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
    """Start command"""
    keyboard = [
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("📩 Help", callback_data="help")]
    ]
    await update.message.reply_text(
        "👋 Namaste! Main **Video Compress Bot** hoon.\n\n"
        "🎥 Mujhe koi video bhejo, main usse compress karke dunga.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📌 Simply video bhejo aur main tumhe compressed version dunga.\n\n"
        "⚙️ Features:\n"
        "1️⃣ Auto video detect\n"
        "2️⃣ Compression (FFmpeg)\n"
        "3️⃣ Multiple quality options\n"
        "4️⃣ Progress updates"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text("ℹ️ Ye ek Telegram bot hai jo videos compress karta hai using ffmpeg.")
    elif query.data == "help":
        await help_command(update, context)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video messages"""
    video = update.message.video
    file_id = video.file_id
    file = await context.bot.get_file(file_id)

    await update.message.reply_text("📥 Downloading video...")

    # Save original video
    input_path = "input.mp4"
    output_path = "output.mp4"
    await file.download_to_drive(input_path)

    await update.message.reply_text("⚙️ Compressing video, please wait...")

    # Run ffmpeg to compress video
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-vcodec", "libx264", "-crf", "28", output_path],
            check=True
        )
        await update.message.reply_video(video=open(output_path, "rb"), caption="✅ Compressed video ready!")
    except Exception as e:
        await update.message.reply_text(f"❌ Compression failed: {e}")

    # Cleanup
    for path in [input_path, output_path]:
        if os.path.exists(path):
            os.remove(path)

# ==============================
# Add Handlers
# ==============================
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))
application.add_handler(MessageHandler(filters.Document.VIDEO, handle_video))
application.add_handler(MessageHandler(filters.VideoNote.ALL, handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mp4$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mkv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.avi$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mov$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.flv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.wmv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.webm$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.3gp$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.ts$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.m4v$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.f4v$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mpg$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mpeg$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.ogv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.vob$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.m2ts$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mts$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.divx$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.xvid$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mxf$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.roq$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.nsv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.asf$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.dv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.rm$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.rmvb$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.amv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mp2$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.smk$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.bik$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.yuv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.viv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.fli$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.flc$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.drc$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.qt$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mng$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.thp$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.nsf$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.vcd$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.3g2$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.str$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.svi$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.m1v$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.m2v$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mpe$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.ogm$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.wtv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.trp$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.tp$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mk3d$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mts$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.m2ts$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.3gpp$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.3gp2$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.webp$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.ogx$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mkv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mov$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.avi$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.flv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.wmv$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.ts$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.mp4$"), handle_video))
application.add_handler(MessageHandler(filters.Regex(".*\.m4v$"), handle_video))

application.add_handler(MessageHandler(filters.ALL, handle_video))

application.add_handler(MessageHandler(filters.ALL, handle_video))

application.add_handler(MessageHandler(filters.ALL, handle_video))

application.add_handler(MessageHandler(filters.ALL, handle_video))

application.add_handler(MessageHandler(filters.ALL, handle_video))


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
