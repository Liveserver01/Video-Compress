1) BOT का काम:

- यूज़र से वीडियो लेता है और FFmpeg से compress/transcode करता है.

- Codec: H.265 (libx265) डिफ़ॉल्ट, बाद में H.264 (libx264) भी चुन सकते हैं.

- Resolution विकल्प: 480p / 720p / 1080p (या Source जैसा ही)

- Framerate: Source जैसा ही (हम ffmpeg में -r सेट नहीं कर रहे ताकि source जैसा रहे).

- Preset: medium या low (low = slow preset के बराबर, ज्यादा quality/कम speed)

- Profile (HEVC): main10, Level: 4.0, CRF: 24

- Audio: same as source (copy) या skip (-an)

- Subtitles: same as source (copy) या skip

- Output container: .mkv (subtitles compatibility के लिए बेहतर)



2) Deployment (Render / Docker):

- नीचे requirements.txt, Dockerfile और .env.example दिया हुआ है.

- Render पर “Web Service” के रूप में चलाइए और ‘Start Command’ में: python main.py

- TELEGRAM_BOT_TOKEN env var ज़रूर सेट करें.

- FFmpeg Dockerfile से install हो जाएगा.



3) लोकल रन:

- Python 3.10+

- pip install -r requirements.txt

- FFmpeg system PATH में होना चाहिए (लोकल में खुद install करें).

- .env में TELEGRAM_BOT_TOKEN सेट करें, फिर: python main.py



4) नोट्स:

- Telegram 2GB+ फाइलों के लिए सावधानी रखें; बड़ी फाइलों में प्रोसेसिंग और अपलोड समय ज्यादा होगा.

- Subtitles copy करने पर कंटेनर .mkv उचित है. Telegram में ये ‘document’ की तरह भेजा जाएगा.

- अगर H.264 चाहिए तो /settings से codec बदल सकते हैं.


