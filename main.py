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
#bot = telebot.TeleBot("6969031808:AAEo3LS0cUEJLbd92JnpHitD7rcB4tOi52c")

store=[]

@bot.message_handler(command=["start"])
def start(message):
    pass

def guide(message):
    bot.send_message(message.chat.id, "save\nupdate\nclear\nplay\ncommand\n\npublic downloader\nyt(short or not)\ntiktok\ninstagram\nfacebook")

def clear(message):
    store.clear()
    bot.send_message(message.chat.id, "All work hass been cleared Sir.")

def update(message):
    try:
        bot.send_message(message.chat.id, store)
        bot.send_message(message.chat.id, "Goodluck Sir.")
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(message.chat.id, "No work has been saved Sir..")

def save(message):
    text = message.text
    load = bot.send_message(message.chat.id, "Loading...").message_id
    #what is judas
    target = "save"
    locate = text.find(target)
    after = text[locate + len(target) + 1:]
    title = after.lower()
    title.replace(",", "/n")
    try:
        store.append(title)
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text="all work are saved Sir")
    except:
        bot.send_message(message.chat.id, "Unable to save it Sir..")

def play(message):
    text = message.text
    load = bot.send_message(message.chat.id, "Loading...").message_id
    #what is judas
    target = "play"
    locate = text.find(target)
    after = text[locate + len(target) + 1:]
    title = after.lower()
    try:
        h = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}"
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text=h)
        #pai.playonyt(title)
    except:
        bot.send_message(message.chat.id, "Unable to search for it Sir.")


def tell(message):
    text = message.text
    load = bot.send_message(message.chat.id, "Loading...").message_id
    #what is judas
    target = "is"
    locate = text.find(target)
    after = text[locate + len(target) + 1:]
    key = after
    try:
        h = wiki.summary(key, sentences=3)
        h1 = wiki.search(key)
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text=h)
        bot.send_message(message.chat.id, f"Anything else Sir:/n/n{h1}")

    except wiki.exceptions.PageError:
        h = wiki.search(key)
        
        bot.send_message(message.chat.id, f"Page for {key} cannot be found. Perhaps try again with these keywords:/n/n{h}")
        
#---CV2---#



@bot.message_handler(content_types=["photo"])
def bismillah(message):
    try:
        if not message.photo:
            print("wrong type!")
        if isinstance(message.photo, list) and len(message.photo) > 0:
            gambar = message.photo[-1]
            info = bot.get_file(gambar.file_id)
        else:
            print("Non valid photo was send")

        link = f"https://api.telegram.org/file/bot{bot.token}/{info.file_path}"
        respon = requests.get(link) # download the file

        #save image kekkawan
        with open("imgb.jpg", "wb") as file:
            file.write(respon.content)
            
        img = cv2.imread("imgb.jpg")

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        label = "Human"  # Label text
        # Set the font and size
        font = cv2.FONT_HERSHEY_COMPLEX
        font_scale = 1
        color = (255, 255, 255)  # White text
        thickness = 3

        # Use minSize because for not 
        # bothering with extra-small 
        # dots that would look like STOP signs
        stop_data = cv2.CascadeClassifier('cv2/detect.xml')
        
        found = stop_data.detectMultiScale(img_gray, 
                                        minSize =(20, 20))
        
        # Don't do anything if there's 
        # no sign
        amount_found = len(found)
        
        if amount_found != 0:
            
            # There may be more than one
            # sign in the image
            for (x, y, width, height) in found:
                
                # We draw a green rectangle around
                # every recognized sign
                cv2.rectangle(img_rgb, (x, y), 
                            (x + height, y + width), 
                            (85,142,199), 5)

        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        text_x = x + (width - text_size[0]) // 2  # Center the text
        text_y = y + height + text_size[1] + 5  # Position below the rectangl

        img_rgb = cv2.putText(img_rgb, label, (text_x, text_y), font, font_scale, color, thickness)
        img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB) 
        img = img_rgb
        cv2.imwrite("final.jpg", img)

        with open("final.jpg", "rb") as final:
            bot.send_photo(message.chat.id, final)

        print("Success!")
    except Exception as e:
        print(f"error: {e}")



#---CV2---#

#--- download ---#
def t(message):
    text = message.text
    if "http" not in message.text.lower():
        return
    elif "http" in message.text.lower():
        if "download" in text.lower():
            load = bot.send_message(message.chat.id, "Downloading...").message_id
            target = "download"
            locate = text.find(target)
            after = text[locate + len(target) + 1:]
            link = after
        elif "download" not in text.lower():
            link = text
            load = bot.send_message(message.chat.id, "Downloading...").message_id
        try:
            app = link.split("/")
            app = app[2]
            print(app)
        except IndexError:
            return

        if "tiktok" in app:
                # tiktok
            try:
                # Specify the TikTok video URL
                tiktok_url = link  # Replace with your video URL
                folder = "download/"
                #folder = "download/"
                # Configure yt-dlp options
                ydl_opts = {
                    'outtmpl': f'{folder}/%(title)s.%(ext)s',  # Specify the download directory
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Get best quality
                    'noplaylist': True,  # Download only the video, not any playlists or extra content
                }

                # Download the video
                with y.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([tiktok_url])
                videof = os.listdir(folder)
                vfile = None

                for file in videof:
                    if file.endswith(".mp4"):
                        vfile = os.path.join(folder, file)
                        break
                
                if vfile:
                    with open(vfile, "rb") as video:
                        media = telebot.types.InputMediaVideo(video, "Here you go Sir.")
                        bot.edit_message_media(media, message.chat.id, load)
                        print("video sent Successfully")
                        os.remove(vfile)
            except y.DownloadError:
                bot.send_message(message.chat.id, f"Link may be unrecognizable Sir.")




        elif "youtu.be" or "youtube" in app:
            try:
                folder = "download/"

                ydl_opts = {
                    'outtmpl': f'{folder}/%(title)s.%(ext)s',  # Specify the download directory
                    'format': "best",  # Get best quality
                }

                with y.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])
                videof = os.listdir(folder)
                vfile = None
                mp4_files = [file for file in videof if file.endswith(".mp4")]
                if mp4_files:  # Check if the list is not empty
                    # Sort by modification time to find the most recently downloaded video
                    vfile = max(mp4_files, key=lambda x: os.path.getmtime(os.path.join(folder, x)))

                for file in videof:
                    if file.endswith(".mp4"):
                        vfile = os.path.join(folder, file)
                        break
                
                if vfile:
                    try:
                        with open(vfile, "rb") as video:
                            media = telebot.types.InputMediaVideo(video, "Here you go Sir.")
                            bot.edit_message_media(media, message.chat.id, load)
                            print("video sent Successfully")
                    finally:
                        if os.path.exists(vfile):
                            os.remove(vfile)
                            print(f"Deleted the video file: {vfile}")

            except y.DownloadError:
                bot.send_message(message.chat.id, f"Link may be unrecognizable Sir.")

        elif "instagram" in app:
            try:
                folder = "download/"

                ydl_opts = {
                    'outtmpl': f'{folder}/%(title)s.%(ext)s',  # Specify the download directory
                    'format': "best",  # Get best quality
                }

                with y.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])
                videof = os.listdir(folder)
                vfile = None
                mp4_files = [file for file in videof if file.endswith(".mp4")]
                if mp4_files:  # Check if the list is not empty
                    # Sort by modification time to find the most recently downloaded video
                    vfile = max(mp4_files, key=lambda x: os.path.getmtime(os.path.join(folder, x)))

                for file in videof:
                    if file.endswith(".mp4"):
                        vfile = os.path.join(folder, file)
                        break
                
                if vfile:
                    try:
                        with open(vfile, "rb") as video:
                            media = telebot.types.InputMediaVideo(video, "Here you go Sir.")
                            bot.edit_message_media(media, message.chat.id, load)
                            print("video sent Successfully")
                    finally:
                        if os.path.exists(vfile):
                            os.remove(vfile)
                            print(f"Deleted the video file: {vfile}")
        
            except y.DownloadError:
                bot.send_message(message.chat.id, f"Link may be unrecognizable Sir.")
        elif "facebook" in app:
            try:
                folder = "download/"

                ydl_opts = {
                    'outtmpl': f'{folder}/%(title)s.%(ext)s',  # Specify the download directory
                    'format': "best",  # Get best quality
                }

                with y.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])
                videof = os.listdir(folder)
                vfile = None
                mp4_files = [file for file in videof if file.endswith(".mp4")]
                if mp4_files:  # Check if the list is not empty
                    # Sort by modification time to find the most recently downloaded video
                    vfile = max(mp4_files, key=lambda x: os.path.getmtime(os.path.join(folder, x)))

                for file in videof:
                    if file.endswith(".mp4"):
                        vfile = os.path.join(folder, file)
                        break
                
                if vfile:
                    try:
                        with open(vfile, "rb") as video:
                            media = telebot.types.InputMediaVideo(video, "Here you go Sir.")
                            bot.edit_message_media(media, message.chat.id, load)
                            print("video sent Successfully")
                    finally:
                        if os.path.exists(vfile):
                            os.remove(vfile)
                            print(f"Deleted the video file: {vfile}")
            except y.DownloadError:
                bot.send_message(message.chat.id, f"Link may be unrecognizable Sir.")
#---tt download---#

@bot.message_handler(func=lambda message: message.text is not None and not message.photo)
def take_command(message):
    print(f"message: {message.text}")
    command = message.text
    if "connor" in message.text.lower():
        print(message.text)
        

        #---Basic Respond---#

        if ("hey connor") in command.lower():
            bot.send_message(message.chat.id, "Yes sir, May I help you?")

        #---Search Wikipedia---#

    elif ("what is") in command.lower():
        tell(message)
    
        #---Play youtube---#

    elif "play" in command.lower():
        play(message)
    elif "save" in command.lower():
        save(message)
    elif "update" in command.lower():
        update(message)
    elif "clear" in command.lower():
        clear(message)
    elif "command" in command.lower():
        guide(message)
    else:
        t(message)






bot.infinity_polling()
