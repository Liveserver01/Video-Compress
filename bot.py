import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from waitress import serve

# ================= CONFIG =================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "https://video-compress.onrender.com")
PORT = int(os.getenv("PORT", 5000))

# ================= FLASK APP ==============
flask_app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# ================= HANDLERS ===============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚙ Settings", callback_data="open_settings")],
        [InlineKeyboardButton("🎥 Send a Video", callback_data="send_video")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome! Send me a video to compress.", reply_markup=reply_markup)

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙ Settings are under construction.")

async def on_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("⚙ Settings clicked!")

async def on_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("✅ Confirm clicked!")

async def on_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Got your video! Processing...")

# ================= REGISTER HANDLERS ======
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("settings", settings_cmd))
application.add_handler(CallbackQueryHandler(on_settings_callback, pattern="^(toggle_|cycle_|reset_|close_|open_settings)$"))
application.add_handler(CallbackQueryHandler(on_confirm_callback, pattern="^(do_compress|cancel_job|send_video)$"))
application.add_handler(MessageHandler(filters.VIDEO | filters.Document.MimeType("video/"), on_video))

# ================= WEBHOOK ================
@flask_app.post(f"/{BOT_TOKEN}")
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

async def init_bot():
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}")

# ================= MAIN ===================
if __name__ == "__main__":
    asyncio.run(init_bot())
    serve(flask_app, host="0.0.0.0", port=PORT)
