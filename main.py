import telebot
import datetime
from dotenv import load_dotenv
import wikipedia as wiki
import webbrowser
import os
import requests
import cv2

load_dotenv()
API_KEY = os.getenv("API_KEY")
bot = telebot.TeleBot(API_KEY)

store=[]

@bot.message_handler(command=["start"])
def start(message):
    pass

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
    title = after
    title = title.replace(",", "\n")
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
        bot.send_message(message.chat.id, f"Anything else Sir:\n\n{h1}")

    except wiki.exceptions.PageError:
        h = wiki.search(key)
        
        bot.send_message(message.chat.id, f"Page for {key} cannot be found. Perhaps try again with these keywords:\n\n{h}")
        
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
        thickness = 1

        # Use minSize because for not 
        # bothering with extra-small 
        # dots that would look like STOP signs
        stop_data = cv2.CascadeClassifier('detect.xml')
        
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
                            (85,142,199), 2)

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

@bot.message_handler(func=lambda message: message.text is not None and not message.photo)
def take_command(message):
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
    else:
        pass






bot.infinity_polling()
