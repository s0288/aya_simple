"""
Handle outgoing messages.
"""
import urllib
import requests
import json
from utils import load_users, URL, write_user_to_db, write_msg_to_db, convert_secs_to_datetime, get_time_since_fasting_start, write_event_to_db

USER_DICT = load_users()

def find_response(telegram_id, message_text):
    """
    Depending on the user's input, send appropriate response.
    :param telegram_id: Telegram ID of user
    :param message_text: text of incoming message_text
    :return: None
    """
    first_word = message_text.split(' ')[0].lower()
    event_name=None
    if first_word == "/start":
        outgoing_txt = _get_rules()
        event_name="start"
    elif first_word == '/name':
        name = message_text.split(' ')[1]
        if name in USER_DICT.values():
            outgoing_txt = "Name bereits vergeben. Bitte wähle einen anderen mit /name [dein Name]"
        else:
            outgoing_txt = f"Willkommen, {name}"
            USER_DICT[telegram_id] = name
            write_user_to_db(telegram_id, name)
            event_name="set_name"
    elif first_word == "/fasten":
        _, hours_since_fasting_start_as_text = get_time_since_fasting_start(telegram_id)
        if hours_since_fasting_start_as_text:
            outgoing_txt = "Du fastest seit " + hours_since_fasting_start_as_text + "."
            event_name="fast_info"
        else:
            outgoing_txt = "Ich habe das Fasten gestartet. Viel Erfolg 🙂."
            event_name="fast_start"
    elif first_word == "/ende":
        hours_since_fasting_start_as_float, hours_since_fasting_start_as_text = get_time_since_fasting_start(telegram_id)
        if hours_since_fasting_start_as_text:
            outgoing_txt = "Ich habe dein Fasten beendet. Du hast " + hours_since_fasting_start_as_text + " gefastet. Glückwünsch 🙂."
            event_name="fast_end"
            write_event_to_db(telegram_id, event_name, hours_since_fasting_start_as_float)
        else:
            outgoing_txt = "Aktuell fastest du nicht. Beginne das Fasten mit /fasten."
    elif first_word == "/rezepte":
        outgoing_txt = "Hier sind ein paar Rezept-Ideen: https://s0288.github.io/strowan_recipes/alle-rezepte/"
        event_name="recipes"
    else:
        outgoing_txt = _get_rules()
        event_name="default_fallback"
    _send_message_to_telegram(telegram_id, outgoing_txt, event_name=event_name)

def _get_rules():
    """
    At start or whenever the user is interested, send the bot's description.
    :return: Text that explains rules of bot.
    """
    txt = "Hallo 🙂. Ich helfe dir zu fasten.\n"
    txt += "Beachte hierfür:\n\n"
    txt += "- 1.) Gib /name und einen Namen deiner Wahl ein:\n"
    txt += "Bsp.: /name alex\n\n"
    txt += "- 2.) Schicke mir einen Befehl:\n"
    txt += "Diese Befehle gibt es: /fasten, /ende, /rezepte, /name."
    return txt


def _send_message_to_telegram(chat_id, message_text, inline_keyboard=None, event_name=None):
    """
    Send message_text to Telegram endpoint. More details here: https://core.telegram.org/bots/api#sendmessage
    :param chat_id: chat id of user
    :param message_text: text of incoming message_text
    :param inline_keyboard: provide inline keyboard (optional)
    :return: None
    """
    parsed_message = urllib.parse.quote_plus(message_text)
    url = URL + f"sendMessage?text={parsed_message}&chat_id={chat_id}"
    url += "&parse_mode=HTML&disable_web_page_preview=true"
    if inline_keyboard:
        url += f"&reply_markup={inline_keyboard}"
    else:
        url += "&reply_markup={\"remove_keyboard\":%20true}"
    response=requests.get(url) # post msg to Telegram server
    # create separate function for this
    chat_id, telegram_id, message_text, timestamp_received = _extract_response(json.loads(response.content.decode("utf8")))
    write_msg_to_db(chat_id, telegram_id, message_text, timestamp_received, event_name=event_name)


def _extract_response(response):
    """
    Extract message elements from Telegram response for outgoing message.
    :param response: response of Telegram's sendMessage() endpoint
    :type response: dict
    :return: chat_id, telegram_id, message_text, timestamp_received
    :rtype: int, str, timestamp
    """
    chat_id = response["result"]["chat"]["id"]
    telegram_id = response["result"]["from"]["id"]
    message_text = response["result"]["text"]
    timestamp_received = convert_secs_to_datetime(response["result"]["date"])
    return chat_id, telegram_id, message_text, timestamp_received

