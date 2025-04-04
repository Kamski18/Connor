import telebot
from dotenv import load_dotenv
import wikipedia as wiki
import os
import requests
import cv2
import yt_dlp as y

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

store = []

@bot.message_handler(commands=["start"])
def start(message):
    pass

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
        bot.send_message(message.chat.id, store)
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

def download_media(message):
    text = message.text
    if text.lower().startswith("mp3 "):
        link = text.partition("mp3 ")[2]
        load = bot.send_message(message.chat.id, "Downloading audio...").message_id

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with y.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            files = os.listdir('downloads')
            for file in files:
                if file.endswith('.mp3'):
                    file_path = os.path.join('downloads', file)
                    with open(file_path, "rb") as audio:
                        bot.send_audio(message.chat.id, audio)
                    os.remove(file_path)
                    break
        except Exception as e:
            bot.send_message(message.chat.id, f"Download failed: {e}")
    else:
        load = bot.send_message(message.chat.id, "Downloading...").message_id

        try:
            ydl_opts = {
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'best'
            }
            with y.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            files = os.listdir('downloads')
            for file in files:
                if file.endswith(('.mp4', '.mp3')):
                    file_path = os.path.join('downloads', file)
                    with open(file_path, "rb") as media:
                        bot.send_document(message.chat.id, media)
                    os.remove(file_path)
                    break
        except Exception as e:
            bot.send_message(message.chat.id, f"Download failed: {e}")

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
    elif "http" or "mp3"in message.text.lower():
        download_media(message)
    else:
        pass

bot.infinity_polling()
