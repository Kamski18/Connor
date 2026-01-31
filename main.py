import os
import uuid
import shutil
import telebot
from dotenv import load_dotenv
import yt_dlp

load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not set in environment variables")

bot = telebot.TeleBot(API_KEY, parse_mode="HTML")


# ---------- HELP / START ----------
@bot.message_handler(commands=["start", "help"])
def guide(message):
    commands = (
        "<b>Commands:</b>\n"
        "play <song name> — Get YouTube search link\n"
        "mp3 <youtube url> — Download audio\n"
        "<youtube/tiktok/instagram/facebook url> — Download video"
    )
    bot.reply_to(message, commands)


# ---------- YOUTUBE SEARCH ----------
def play(message):
    query = message.text.partition("play ")[2].strip()
    if not query:
        bot.reply_to(message, "Usage: play <song name>")
        return

    link = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    bot.reply_to(message, link)


# ---------- DOWNLOAD HANDLER ----------
def download_media(message):
    text = message.text.strip()
    user_id = message.from_user.id

    # Create unique temp directory per request
    temp_dir = f"downloads/{user_id}_{uuid.uuid4().hex}"
    os.makedirs(temp_dir, exist_ok=True)

    is_mp3 = text.lower().startswith("mp3 ")
    link = text.partition(" ")[2] if is_mp3 else text

    status = bot.reply_to(message, "⏳ Downloading...")

    try:
        ydl_opts = {
            "outtmpl": f"{temp_dir}/%(title)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "restrictfilenames": True,
            "format": "bestaudio/best" if is_mp3 else "bestvideo+bestaudio/best",
        }

        if is_mp3:
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # Find downloaded file
        file_path = None
        for f in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, f)
            break

        if not file_path:
            raise Exception("File not found after download.")

        with open(file_path, "rb") as media:
            if is_mp3:
                bot.send_audio(message.chat.id, media)
            else:
                bot.send_document(message.chat.id, media)

        bot.delete_message(message.chat.id, status.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Download failed:\n<code>{e}</code>",
                              message.chat.id, status.message_id)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ---------- MESSAGE ROUTER ----------
@bot.message_handler(func=lambda msg: True, content_types=["text"])
def handle_messages(message):
    text = message.text.lower()

    if text.startswith("play "):
        play(message)

    elif text.startswith("mp3 ") or text.startswith("http"):
        download_media(message)

    elif text in ["command", "commands", "help"]:
        guide(message)


print("Bot is running...")
bot.infinity_polling(skip_pending=True)