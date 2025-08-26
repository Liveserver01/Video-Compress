import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # Render environment se token read karega

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video 🎥 and I will compress it using FFmpeg")

# Handle Video Upload
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video
    file = await context.bot.get_file(video.file_id)
    file_path = f"downloads/{video.file_id}.mp4"
    os.makedirs("downloads", exist_ok=True)
    await file.download_to_drive(file_path)

    # Options for codec
    keyboard = [
        [
            InlineKeyboardButton("H.265 (HEVC)", callback_data=f"codec_h265|{file_path}"),
            InlineKeyboardButton("H.264", callback_data=f"codec_h264|{file_path}")
        ]
    ]
    await update.message.reply_text("Choose codec:", reply_markup=InlineKeyboardMarkup(keyboard))

# Handle Codec and Resolution Selection
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("|")
    action = data[0]
    file_path = data[1]

    if action.startswith("codec_"):
        codec = action.split("_")[1]
        keyboard = [
            [
                InlineKeyboardButton("480p", callback_data=f"res_480|{codec}|{file_path}"),
                InlineKeyboardButton("720p", callback_data=f"res_720|{codec}|{file_path}"),
                InlineKeyboardButton("1080p", callback_data=f"res_1080|{codec}|{file_path}")
            ]
        ]
        await query.edit_message_text("Choose resolution:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif action.startswith("res_"):
        res = action.split("_")[1]
        codec = data[1]
        file_path = data[2]

        output_file = f"compressed_{os.path.basename(file_path)}"

        # Codec selection
        if codec == "h265":
            vcodec = "libx265"
            profile = "-profile:v main10 -level 4.0"
        else:
            vcodec = "libx264"
            profile = "-profile:v high -level 4.0"

        # Resolution scaling
        scale = ""
        if res == "480":
            scale = "-vf scale=-1:480"
        elif res == "720":
            scale = "-vf scale=-1:720"
        elif res == "1080":
            scale = "-vf scale=-1:1080"

        cmd = f"ffmpeg -i {file_path} {scale} -c:v {vcodec} -preset medium {profile} -crf 24 -c:a copy {output_file}"

        # Run ffmpeg
        subprocess.run(cmd, shell=True)

        await query.edit_message_text("✅ Compression done! Uploading...")

        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(output_file, "rb"))

        # Cleanup
        os.remove(file_path)
        os.remove(output_file)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
