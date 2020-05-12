import json
import requests
import time
import urllib
import os
from dbhelper import DBHelper

db = DBHelper()

TOKEN = os.environ.get('TOKEN')
baseUrl = os.environ.get('BASE_URL')           # Added a few improvement, instead of --
									# URL "https://api.telegram.org/bot{}/".format(TOKEN)
URL = baseUrl.format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

'''
def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)
        if text == "/done":  # Command, once all To-Do listing finished
                keyboard = build_keyboard(items)
                send_message("Select an item to delete 📝 from the below list, If no Items appear select,  /start to add ", chat, keyboard)
        elif text == "/start":  # Command, to star To-Do listing finished
            send_message("Welcome to your personal To-Do list📋🧐. Send any text to me (--Example: Bring Veggi's from Market & Tap on send) and I'll store 💾 it as an item. To remove items select  /done ", chat)
        elif text.startswith("/"):
            continue
        elif text in items:
# Added a feature, BELOW If..Else{} when we try to Delete an Empty To-Do list 
            #if db.cnt != None:         
                db.delete_item(text, chat)
                items = db.get_items(chat)
                keyboard = build_keyboard(items)  #
                send_message("Yipeee🐒, Your To-Do List is cleared by one Item, Chill!! Select an item to delete 📝 or /start to add the new item", chat, keyboard)       
            #else:
             #   db.delete_item(text, chat)  #
              #  keyboard = build_keyboard(items)
               # send_message("There are no Items 📝 to delete. Start adding an action to your list", chat, keyboard)
        else:
            db.add_item(text, chat)
            items = db.get_items(chat)
            message = "\n".join(items)
            send_message(message, chat)
'''

def handle_updates(updates):
    for update in updates['result']:
        text = update['message']['text']
        chat_id = update['message']['chat']['id']
        items = DB.get_items(chat_id)
        if text == '/start':
            send_message("Welcome to your personal To-Do list📋🧐.\n Send anything that needs to be included in the list to me \n (--Example: Bring Veggi's from Market & Tap on send) and \n I'll store 💾 it as an item.\n To remove items select  /done ", chat)
        elif text == '/done':
		keyboard = build_keyboard(items)
		send_message("Select an item to delete 📝 from the below list or \n select,  /start to add ", chat, keyboard)
        elif text == '/show':
            send_message(chat_id, 'Here is your To-Do List:\n\n')
            send_message(chat_id, '\n'.join(items))
        elif text.startswith('/'):
            continue
        elif text in items:
            DB.delete_item(chat_id, text)
            items = DB.get_items(chat_id)
            send_message(chat_id, 'Yipeee🐒, Item --"{}" marked as completed.\n Select an item to delete 📝 or /start to add the new item'.format(text))
        else:
            DB.add_item(chat_id, text)
            items = DB.get_items(chat_id)
            send_message(chat_id, 'Item "{}" Added to TODO List'.format(text))


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + \
        "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def main():
    db.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
