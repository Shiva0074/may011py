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

def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)
        if text == "/done":  # Command, once all To-Do listing finished
            keyboard = build_keyboard(items)
            send_message("Select an item to delete from the below list 📋.\nIf no Items appear,\tAdd them by \tselect--\t/start", chat, keyboard)
        elif text == "/start":  # Command, to star To-Do listing finished
            send_message("Welcome to your personal To-Do list 📋.\n\n(--Example: Bring Veggi's from Market & Tap on send)\n\t\t\t\t\t\t\t\t\t\t\t----Options----\nTo add New Items, select--\t/start\nTo remove Items, select--\t /done \nTo display saved Items, select--\t/show\n\nStart sending your Items To-Do,\tHere below......!", chat)
        elif text == "/show":
            send_message("\n\t\tYour To-Do List📋:\n\n", chat)
            send_message("\n".join(items), chat)         
        elif text.startswith("/"):
            continue
        elif text in items:        
            db.delete_item(text, chat)
            items = db.get_items(chat)
            send_message('Item "{}" Completed from List📜,\tYipeee🐒.\n\n(\tTo add New Item,select--\t/start\t)'.format(text), chat)
        else:
            db.add_item(text, chat)
            items = db.get_items(chat)
            send_message('Item "{}" Added to your To-Do List📜.\n\n(\tTo remove,select--\t/done\nTo display Items,select--\t/show\t)'.format(text), chat)

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
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
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
