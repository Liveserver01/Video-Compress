import os 
import subprocess 
import tempfile 
from flask import Flask 
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton 
from telegram.ext import ( 
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters, 
    ContextTypes, 
)

================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN") 
PORT = int(os.environ.get("PORT", 5000))

Flask app to keep service alive

app = Flask(name)

@app.route("/") 
def home(): 
    return "✅ Telegram FFmpeg Bot is running!"

============== TELEGRAM BOT ==============

Store user settings

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
    await query.edit_message_text(
        "⚙️ Default settings set ho gayi hain:\n"
        "Codec: H.265 (HEVC)\n"
        "Resolution: 720p\n"
        "Preset: medium\n"
        "CRF: 24\n"
        "Audio: same as source\n"
        "Subtitles: same as source\n\n"
        "Ab mujhe apna video bhejiye 📩"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.from_user.id 
    if user_id not in user_settings: 
        await update.message.reply_text("⚠️ Pehle /start kijiye aur settings choose kijiye.") 
        return

file = await context.bot.get_file(update.message.video.file_id)
input_path = tempfile.mktemp(suffix=".mp4")
output_path = tempfile.mktemp(suffix=".mp4")
await file.download_to_drive(input_path)

settings = user_settings[user_id]
resolution_map = {"480p": "854x480", "720p": "1280x720", "1080p": "1920x1080"}
resolution = resolution_map.get(settings["resolution"], "1280x720")

ffmpeg_cmd = [
    "ffmpeg",
    "-i", input_path,
    "-c:v", settings["codec"],
    "-preset", settings["preset"],
    "-profile:v", "main10",
    "-level:v", "4.0",
    "-crf", str(settings["crf"]),
    "-vf", f"scale={resolution}",
    "-c:a", settings["audio"],
    "-c:s", settings["subs"],
    output_path,
]

try:
    await update.message.reply_text("⏳ Compressing video, please wait...")
    subprocess.run(ffmpeg_cmd, check=True)

    await update.message.reply_video(video=open(output_path, "rb"), caption="✅ Compression Done!")
except Exception as e:
    await update.message.reply_text(f"❌ Error during compression: {e}")
finally:
    for f in [input_path, output_path]:
        try:
            os.remove(f)
        except:
            pass

============== MAIN RUNNER ==============

async def main(): 
    application = Application.builder().token(BOT_TOKEN).build() 
    application.add_handler(CommandHandler("start", start)) 
    application.add_handler(CallbackQueryHandler(button)) 
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))

await application.start()
await application.updater.start_polling()
await application.updater.idle()

if name == "main": 
    import threading, asyncio

def run_bot():
    asyncio.run(main())

threading.Thread(target=run_bot).start()
app.run(host="0.0.0.0", port=PORT)

