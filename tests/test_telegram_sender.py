"""
Test functions for sender of outgoing messages to Telegram.
"""
import pytest
import src.telegram_sender as ts

@pytest.fixture
def outgoing_message():
    outgoing_message = {
        'ok': True, 
        'result': {
            'message_id': 1413, 
            'from': {
                'id': 987654321, 'is_bot': True, 
                'first_name': 'TEST_NAME', 'username': 'TEST_BOT'
            }, 
            'chat': {'id': 123456789, 'first_name': 'FIRST_NAME', 'type': 'private'}, 
            'date': 1650282548, 
            'text': 'Hallo, ich bin ein Chatbot.', 
            'entities': [
                {'offset': 86, 'length': 5, 'type': 'bot_command'}, 
                {'offset': 183, 'length': 5, 'type': 'bot_command'}
            ]
        }
    }
    return outgoing_message

def test_telegram_sender__extract_response(outgoing_message):
    assert ts._extract_response(outgoing_message) == (123456789, 987654321, 'Hallo, ich bin ein Chatbot.', '2022-04-18 13:49:08')

