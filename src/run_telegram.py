#!/usr/bin/python3.6
# coding: utf8
"""
Open and maintain connection to Telegram chatbot.
"""

import logging
import time
import sys
from telegram_listener import get_incoming_message_and_next_update_id, extract_main

def open_connection_to_telegram_chatbot(chat_id=None):
    # last_update_id is used to make sure that messages are only retrieved once
    next_update_id = None
    logging.info(f"starting Telegram_Listener")
    while True:
        try:
            incoming_message, next_update_id = get_incoming_message_and_next_update_id(offset=next_update_id)
            if incoming_message:
                chat_id, message_text = extract_main(incoming_message)
        except Exception as e:
            logging.exception(e)
        time.sleep(0.5)
        sys.stdout.write('.'); sys.stdout.flush()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO)
    open_connection_to_telegram_chatbot()
