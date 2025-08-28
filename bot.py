import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

# --- ENVIRONMENT ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # e.g. https://video-compress-jobi.onrender.com
PORT = int(os.getenv("PORT", 10000))

# --- GLOBAL LOOP ---
loop = asyncio.get_event_loop()

# --- Flask app ---
flask_app = Flask(__name__)

# --- Telegram Application ---
application = ApplicationBuilder().token(BOT_TOKEN).build()


# ===== Handlers =====
async def start(update: Update, context):
    await update.message.reply_text("✅ Bot चालू है! Video भेजो compress करने के लिए.")


async def echo_video(update: Update, context):
    await update.message.reply_text("📥 Video मिला! Compression demo mode में है.")


application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.VIDEO, echo_video))


# ===== Flask Webhook =====
@flask_app.post(f"/webhook/{BOT_TOKEN}")
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # update को asyncio loop में डालो
    loop.create_task(application.process_update(update))
    return "ok"


# ===== Set Webhook =====
async def set_webhook():
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_webhook(url=f"{RENDER_URL}/webhook/{BOT_TOKEN}")


if __name__ == "__main__":
    # पहले webhook सेट करो
    loop.run_until_complete(set_webhook())

    # Flask सर्वर चलाओ (main thread में)
    flask_app.run(host="0.0.0.0", port=PORT)
