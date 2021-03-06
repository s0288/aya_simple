"""
Functions to listen for incoming messages from Telegram.
"""

import os
from os.path import join, dirname
import requests
import json
import logging
from datetime import datetime

from utils import URL, write_msg_to_db, convert_secs_to_datetime


def get_incoming_message_and_next_update_id(offset=None):
    """
    Retrieve incoming msg.
    Telegram saves all incoming msgs into an update json that looks like this:
        {"ok":True,"result":[
            {"update_id":161176028,"message":{"message_id":811,
                "from":{"id":TELEGRAM_USER_ID,"is_bot":False,"first_name":"TELEGRAM_FIRST_NAME","language_code":"en"},
                "chat":{"id":TELEGRAM_USER_ID,"first_name":"TELEGRAM_FIRST_NAME","type":"private"},
                "date":1610819511,"text":"Hi there"}},
            {"update_id":161176029, ...}
        ]}
    
    It is possible that Telegram does not update the result json before polling occurs again. 
    To prevent retrieving the same msg twice, ignore the already retrieved update_ids with next_update_id.

    :param offset:  ignore all update_ids until the requested offset
    :type offset:   int
    :return:        
        incoming message in Telegram format
        + next update id (min(update_id)+1 in incoming msgs)
    :rtype: json, int
    """
    url = URL + "getUpdates?timeout=600"
    if offset:
        url += "&offset={}".format(offset)
    
    js = _call_telegram_url(url)
    incoming_message, next_update_id = _get_incoming_message_and_next_update_id(js)
    
    return incoming_message, next_update_id


def _call_telegram_url(url):
    """
    Call Telegram url and return response.
    :param url: one of several endpoints to Telegram api.
        More details here: https://core.telegram.org/bots/api#getupdates
        and here: https://core.telegram.org/bots/api#answercallbackquery
    :type url:  str
    :return:    incoming msgs
    :rtype:     json
    """
    response = requests.get(url)
    content = response.content.decode("utf8")
    js = json.loads(content)
    return js


def _get_incoming_message_and_next_update_id(js):
    """
    :param js: json that contains one or many incoming messages
    :return: json that contains only one message
    :rtype: json
    """
    if any(js["result"]):
        update_id = min([row["update_id"] for row in js["result"]])
        incoming_message = [row for row in js["result"] if row["update_id"] == update_id][0]
        return incoming_message, update_id+1
    else: 
        return None, None


def extract_main(incoming_message):
    """
    Extract chat_id and text from incoming message. 
    Save message with update_id and return chat_id and message_text.
    :param incoming_message: incoming message as json, in Telegram message format.
    :return: chat_id, text of incoming message
    :rtype: int, str
    """
    extraction_method = _set_extraction_method(incoming_message)
    if extraction_method == 'do_not_extract':
        return None, None, None
    if extraction_method == 'extract_message':
        chat_id, update_id, message_text, timestamp_received = _extract_message(incoming_message)
    elif extraction_method == 'extract_callback':
        _answer_callback(incoming_message['callback_query']['id'])
        chat_id, update_id, message_text, timestamp_received = _extract_callback(incoming_message)
    write_msg_to_db(chat_id, chat_id, message_text, timestamp_received, update_id=update_id)
    return chat_id, message_text


def _set_extraction_method(incoming_message):
    """
    At least these extraction methods exist: [message, callback, not-to-be-extracted content]
    :param incoming_message: incoming message as json, in Telegram message format.
    :return: extraction method
    :rtype: str
    """
    if incoming_message.get('message'):
        if any(incoming_message["message"].get(key) for key in ['group_chat_created', 'new_chat_participant', 'left_chat_participant']): 
            logging.info(f"received an out-of-the-ordinary message: {incoming_message}")
            return 'do_not_extract'
        return 'extract_message'
    elif incoming_message.get('callback_query'):
        return 'extract_callback'
    else:
        return 'do_not_extract'


def _extract_message(incoming_message):
    """
    If message is an img or document, only return Telegram's file id.
    :param incoming_message: incoming message as dict
    :return: chat_id, update_id, text of incoming message
    :rtype: int, int, str
    """
    chat_id = incoming_message["message"]["chat"]["id"]
    update_id = incoming_message["update_id"]
    timestamp_received = convert_secs_to_datetime(incoming_message["message"]["date"])
    if incoming_message["message"].get('text'):
        message_text = incoming_message["message"]["text"]
    elif incoming_message["message"].get('document'): # e.g. pdf
        message_text = 'file: ' + incoming_message["message"]["document"]["file_id"]
    elif incoming_message["message"].get('photo'): # e.g. jpg
        try:
            message_text = 'file: ' + incoming_message["message"]["photo"][3]["file_id"]
        except:
            message_text = 'file: ' + incoming_message["message"]["photo"][0]["file_id"]
    return chat_id, update_id, message_text, timestamp_received


def _answer_callback(callback_query_id):
    """
    answering a callback is necessary to unfreeze the user's telegram chat (e.g. for inline buttons)
    :param callback_query_id: 
    :return: None
    """
    url = URL + f"answerCallbackQuery?callback_query_id={callback_query_id}"
    _call_telegram_url(url)


def _extract_callback(incoming_message):
    """
    :param incoming_message: incoming message as json, in Telegram message format.
    :return: chat_id, update_id, text of incoming message
    :rtype: int, int, str
    """
    chat_id = incoming_message["callback_query"]["message"]["chat"]["id"]
    update_id = incoming_message["update_id"]
    message_text = incoming_message["callback_query"]["data"]
    timestamp_received = convert_secs_to_datetime(incoming_message["callback_query"]["message"]["date"])
    return chat_id, update_id, message_text, timestamp_received
