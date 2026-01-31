import os
from dotenv import load_dotenv
import telebot
import yt_dlp

load_dotenv()

TOKEN = os.getenv("API_KEY")
bot = telebot.TeleBot(TOKEN, parse_mode=None)  # Disable HTML parsing

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ===================== COMMANDS =====================

@bot.message_handler(commands=["start", "help", "command"])
def guide(message):
    commands = (
        "Commands:\n"
        "play - song name → Get YouTube search link\n"
        "mp3 youtube_url → Download audio\n"
        "Send a video URL → Download video"
    )
    bot.reply_to(message, commands)


# ===================== PLAY SEARCH =====================

def play(message):
    query = message.text.partition("play ")[2].strip()
    if not query:
        bot.reply_to(message, "Give a song name after 'play'")
        return

    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    bot.reply_to(message, search_url)


# ===================== DOWNLOADERS =====================

def download_audio(chat_id, url, status_msg_id):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
                "cookiefile": "cookies.txt" 
            }],
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith(".mp3"):
                path = os.path.join(DOWNLOAD_DIR, file)
                with open(path, "rb") as audio:
                    bot.send_audio(chat_id, audio)
                os.remove(path)
                break

        bot.delete_message(chat_id, status_msg_id)

    except Exception as e:
        bot.send_message(chat_id, f"Audio download failed:\n{e}")


def download_video(chat_id, url, status_msg_id):
    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
            "noplaylist": True,
            "quiet": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir(DOWNLOAD_DIR):
            if file.endswith((".mp4", ".mkv", ".webm")):
                path = os.path.join(DOWNLOAD_DIR, file)
                with open(path, "rb") as vid:
                    bot.send_document(chat_id, vid)
                os.remove(path)
                break

        bot.delete_message(chat_id, status_msg_id)

    except Exception as e:
        bot.send_message(chat_id, f"Video download failed:\n{e}")


# ===================== MESSAGE ROUTER =====================

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    text = message.text.strip()

    # PLAY SEARCH
    if text.lower().startswith("play "):
        play(message)
        return

    # MP3 DOWNLOAD
    if text.lower().startswith("mp3 "):
        url = text.partition("mp3 ")[2].strip()
        status = bot.send_message(message.chat.id, "Downloading audio...")
        download_audio(message.chat.id, url, status.message_id)
        return

    # VIDEO DOWNLOAD (URL DETECT)
    if text.startswith("http"):
        status = bot.send_message(message.chat.id, "Downloading video...")
        download_video(message.chat.id, text, status.message_id)
        return


# ===================== START BOT =====================

print("Bot is running...")

bot.infinity_polling(
    skip_pending=True,
    timeout=30,
    long_polling_timeout=30,
    none_stop=True
)
