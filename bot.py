import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # example: https://video-compress-jobi.onrender.com
PORT = int(os.getenv("PORT", 10000))

# Flask app
flask_app = Flask(__name__)

# Telegram application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# ---- Handlers ----
async def start(update: Update, context):
    await update.message.reply_text("👋 Bot चल पड़ा है! Video भेजो compress करने के लिए.")

async def echo_video(update: Update, context):
    await update.message.reply_text("📥 Video मिल गया! (Compression अभी demo है)")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.VIDEO, echo_video))


# ---- Flask webhook ----
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


# ---- Run ----
async def set_webhook():
    # पहले पुराना webhook हटाओ
    await application.bot.delete_webhook(drop_pending_updates=True)
    # नया webhook लगाओ
    await application.bot.set_webhook(url=f"{RENDER_URL}/webhook/{BOT_TOKEN}")

if __name__ == "__main__":
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=PORT)
