import os
import requests
import cv2
import wikipedia as wiki
import yt_dlp as y
from dotenv import load_dotenv
import telebot

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

# In-memory storage for tasks
store = []

# Command handlers
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Welcome! Type 'command' to see available commands.")

def guide(message):
    bot.send_message(
        message.chat.id,
        "Available commands:\n" \
        "save\nupdate\nclear\nplay\ncommand\n\n" \
        "Public downloader:\nyt (short or not)\ntiktok\ninstagram\nfacebook"
    )

def clear(message):
    store.clear()
    bot.send_message(message.chat.id, "All tasks have been cleared, Sir.")

def update(message):
    if store:
        bot.send_message(message.chat.id, "Saved tasks:\n" + "\n".join(store))
    else:
        bot.send_message(message.chat.id, "No tasks saved, Sir.")

def save(message):
    task = message.text.replace("save", "").strip()
    if task:
        store.append(task)
        bot.send_message(message.chat.id, "Task saved successfully, Sir.")
    else:
        bot.send_message(message.chat.id, "No task provided, Sir.")

def play(message):
    query = message.text.replace("play", "").strip()
    if query:
        youtube_link = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        bot.send_message(message.chat.id, f"Search link: {youtube_link}")
    else:
        bot.send_message(message.chat.id, "No query provided, Sir.")

def tell(message):
    query = message.text.split("is", 1)[-1].strip()
    if query:
        try:
            summary = wiki.summary(query, sentences=3)
            bot.send_message(message.chat.id, summary)
        except wiki.exceptions.PageError:
            suggestions = wiki.search(query)
            bot.send_message(
                message.chat.id, 
                f"No page found for '{query}'. Suggestions:\n" + "\n".join(suggestions)
            )
    else:
        bot.send_message(message.chat.id, "No query provided, Sir.")

# Photo processing handler
@bot.message_handler(content_types=["photo"])
def process_photo(message):
    try:
        photo = message.photo[-1]  # Get the highest resolution photo
        file_info = bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        # Download and process the image
        response = requests.get(file_url)
        with open("temp.jpg", "wb") as file:
            file.write(response.content)

        img = cv2.imread("temp.jpg")
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        stop_data = cv2.CascadeClassifier('detect.xml')
        detections = stop_data.detectMultiScale(img_gray, minSize=(20, 20))

        for (x, y, w, h) in detections:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img, "Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

        cv2.imwrite("result.jpg", img)
        with open("result.jpg", "rb") as result:
            bot.send_photo(message.chat.id, result)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error processing photo: {e}")

# Download handler
def download_content(message):
    url = message.text.split("download", 1)[-1].strip()
    if url:
        bot.send_message(message.chat.id, "Downloading...")
        try:
            folder = "downloads/"
            os.makedirs(folder, exist_ok=True)
            ydl_opts = {'outtmpl': f'{folder}/%(title)s.%(ext)s', 'format': 'best'}

            with y.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            downloaded_files = [
                os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".mp4")
            ]
            if downloaded_files:
                latest_file = max(downloaded_files, key=os.path.getctime)
                with open(latest_file, "rb") as video:
                    bot.send_video(message.chat.id, video)
                os.remove(latest_file)
        except Exception as e:
            bot.send_message(message.chat.id, f"Failed to download: {e}")
    else:
        bot.send_message(message.chat.id, "No URL provided, Sir.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    if "connor" in text:
        bot.send_message(message.chat.id, "Yes, Sir? How can I assist?")
    elif "what is" in text:
        tell(message)
    elif "play" in text:
        play(message)
    elif "save" in text:
        save(message)
    elif "update" in text:
        update(message)
    elif "clear" in text:
        clear(message)
    elif "command" in text:
        guide(message)
    elif "download" in text:
        download_content(message)

bot.infinity_polling()
