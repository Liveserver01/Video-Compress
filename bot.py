import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
APP_URL = os.getenv("RENDER_EXTERNAL_URL")  # e.g. https://video-compress-jobi.onrender.com

# Flask App
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(TOKEN).build()


# Start Command
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("📤 Video भेजें", callback_data="send_video")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 नमस्ते! Video Compression Bot में आपका स्वागत है.\n\n👉 कोई भी video भेजें.", reply_markup=reply_markup)


# Help Command
async def help_command(update: Update, context):
    await update.message.reply_text("बस मुझे कोई भी video भेजें, और मैं उसे compress करके वापस भेज दूँगा ✅")


# Callback Handler
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "send_video":
        await query.edit_message_text("कृपया मुझे कोई video भेजें 🎬")
    elif query.data == "help":
        await query.edit_message_text("ℹ️ Help:\n\n- मुझे video भेजें\n- मैं उसे compress करूँगा\n- और compressed video आपको वापस भेजूँगा ✅")


# Video Handler
async def handle_video(update: Update, context):
    video = update.message.video
    await update.message.reply_text("📥 Video प्राप्त हुआ. Processing शुरू... (Compression code यहाँ जोड़ना है)")


# Handlers Register
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.VIDEO, handle_video))


# Flask route for webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


@app.route("/")
def index():
    return "Bot is running!"


if __name__ == "__main__":
    # Set Webhook
    import asyncio
    async def set_webhook():
        await application.bot.set_webhook(f"{APP_URL}/{TOKEN}")

    asyncio.run(set_webhook())

    # Run Flask
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
