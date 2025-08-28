import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext._utils.types import JSONDict

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")  # example: https://video-compress-jobi.onrender.com/webhook

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# ---------- Bot Handlers ----------
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🎥 Send a Video", callback_data="send_video")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome! Please choose an option:", reply_markup=reply_markup)

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("ℹ️ Send me a video and I’ll help compress it!")

async def handle_video(update: Update, context: CallbackContext):
    await update.message.reply_text("📥 Video received! Processing...")

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == "send_video":
        await query.edit_message_text("📤 Please send me a video now!")
    elif query.data == "help":
        await query.edit_message_text("ℹ️ Just send me any video and I’ll compress it.")

# ---------- Add handlers ----------
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))
application.add_handler(CallbackQueryHandler(button_handler))

# ---------- Flask Route ----------
@app.route("/webhook", methods=["POST"])
def webhook() -> JSONDict:
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        application.update_queue.put_nowait(update)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return {"ok": True}

# ---------- Set Webhook ----------
@app.before_first_request
def set_webhook():
    app.logger.info("Setting webhook...")
    application.bot.set_webhook(url=f"{WEBHOOK_URL}")

# ---------- Main ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
