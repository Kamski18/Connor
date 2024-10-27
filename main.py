import telebot
import datetime
from dotenv import load_dotenv
import wikipedia as wiki
import webbrowser
import os

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
    after = text[locate + len(target) + 2:]
    title = after.lower()
    title.replace(",", "\n")
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
    after = text[locate + len(target) + 2:]
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
    key = after.capitalize()
    try:
        h = wiki.summary(key, sentences=3)
        bot.edit_message_text(chat_id=message.chat.id, message_id=load, text=h)

    except (wiki.exceptions.PageError, wiki.exceptions.DisambiguationError):
        h = wiki.search(key)
        
        bot.send_message(message.chat.id, f"Page for {key} cannot be found. Perhaps try again with these keywords:\n\n{h}")
        


@bot.message_handler(func=lambda message: True)
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
