import telebot
from dotenv import load_dotenv
import wikipedia as wiki
import os
import requests
import cv2
import yt_dlp as y
import re

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

store = []

# Utility function to sanitize and truncate file names
def sanitize_file_name(file_name, max_length=50):
    file_name = re.sub(r'[\\/*?:"<>|]', '_', file_name)  # Replace invalid characters
    return file_name[:max_length]  # Truncate to max length

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Welcome, Sir! Use /command for available commands.")

def guide(message):
    commands = (
        "save\nupdate\nclear\nplay\ncommand\n\npublic downloader\n"
        "yt(short or not)\ntiktok\ninstagram\nfacebook"
    )
    bot.send_message(message.chat.id, commands)

def clear(message):
    store.clear()
    bot.send_message(message.chat.id, "All work has been cleared, Sir.")

def update(message):
    if store:
        bot.send_message(message.chat.id, "\n".join(store))
        bot.send_message(message.chat.id, "Good luck, Sir.")
    else:
        bot.send_message(message.chat.id, "No work has been saved, Sir.")

def save(message):
    text = message.text
    load = bot.send_message(message.chat.id, "Loading...").message_id
    after = text.partition("save ")[2].lower()
    try:
        store.append(after)
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text="All work has been saved, Sir.")
    except Exception:
        bot.send_message(message.chat.id, "Unable to save it, Sir.")

def play(message):
    text = message.text
    load = bot.send_message(message.chat.id, "Loading...").message_id
    after = text.partition("play ")[2].lower()
    try:
        link = f"https://www.youtube.com/results?search_query={after.replace(' ', '+')}"
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text=link)
    except Exception:
        bot.send_message(message.chat.id, "Unable to search for it, Sir.")

def tell(message):
    text = message.text
    load = bot.send_message(message.chat.id, "Loading...").message_id
    after = text.partition("is ")[2]
    try:
        summary = wiki.summary(after, sentences=3)
        suggestions = wiki.search(after)
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text=summary)
        bot.send_message(message.chat.id, f"Anything else, Sir?\n\n{suggestions}")
    except wiki.exceptions.PageError:
        suggestions = wiki.search(after)
        bot.send_message(message.chat.id, f"Page for {after} cannot be found. Try these keywords:\n\n{suggestions}")

@bot.message_handler(content_types=["photo"])
def process_image(message):
    try:
        if not message.photo:
            return
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        file_path = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        response = requests.get(file_path)

        with open("img.jpg", "wb") as file:
            file.write(response.content)

        img = cv2.imread("img.jpg")
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        label = "Human"
        font = cv2.FONT_HERSHEY_COMPLEX
        color = (255, 255, 255)
        thickness = 3
        stop_data = cv2.CascadeClassifier('detect.xml')

        detections = stop_data.detectMultiScale(img_gray, minSize=(20, 20))
        for (x, y, w, h) in detections:
            cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (85, 142, 199), 5)
            text_size = cv2.getTextSize(label, font, 1, thickness)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + h + text_size[1] + 5
            cv2.putText(img_rgb, label, (text_x, text_y), font, 1, color, thickness)

        cv2.imwrite("final.jpg", img_rgb)
        with open("final.jpg", "rb") as final_image:
            bot.send_photo(message.chat.id, final_image)
    except Exception as e:
        print(f"Error processing image: {e}")
        # Make sure to import re for sanitizing file names

def download_media(message):
    text = message.text
    link = text.partition("download ")[2] if "download" in text.lower() else text
    load = bot.send_message(message.chat.id, "Downloading...").message_id

    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'best',
            'noplaylist': True,  # Download only a single video
        }

        with y.YoutubeDL(ydl_opts) as ydl:
            # Extract information without downloading
            info_dict = ydl.extract_info(link, download=False)

            # Check if info_dict is a dictionary and contains 'title'
            if not isinstance(info_dict, dict):
                raise ValueError("Unexpected response format from yt_dlp.")
            if 'title' not in info_dict:
                raise ValueError("Video title not found in the response.")

            title = info_dict.get('title', 'downloaded_video')
            ext = info_dict.get('ext', 'mp4')

            # Sanitize and truncate the file name
            sanitized_title = sanitize_file_name(title)
            ydl_opts['outtmpl'] = f'downloads/{sanitized_title}.%(ext)s'

            # Download the video with the updated template
            ydl.download([link])

            # Locate the downloaded file
            downloaded_files = os.listdir('downloads')
            for file in downloaded_files:
                if file.endswith(('.mp4', '.mp3')):
                    file_path = os.path.join('downloads', file)
                    with open(file_path, "rb") as media:
                        bot.send_document(message.chat.id, media)
                    os.remove(file_path)  # Remove the file after sending
                    break

            bot.edit_message_text(chat_id=message.chat.id, message_id=load, text="Download complete, Sir.")
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text=f"Download failed: {e}")

@bot.message_handler(func=lambda msg: True)
def handle_commands(message):
    if "what is" in message.text.lower():
        tell(message)
    elif "play" in message.text.lower():
        play(message)
    elif "save" in message.text.lower():
        save(message)
    elif "update" in message.text.lower():
        update(message)
    elif "clear" in message.text.lower():
        clear(message)
    elif "command" in message.text.lower():
        guide(message)
    elif "http" in message.text.lower():
        download_media(message)

bot.infinity_polling()
