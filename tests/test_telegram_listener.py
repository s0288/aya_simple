"""
Test functions for listener of incoming messages to Telegram.
"""
import pytest
import src.telegram_listener as tl

@pytest.fixture
def no_incoming_messages():
    return {"ok":True,"result":[]}

@pytest.fixture
def input_multiple_messages():
    multiple_messages = {
        "ok":True,"result":[
            {
                "update_id":161176028,
                "message":{
                    "message_id":811,
                    "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
                    "chat":{"id":123456789,"first_name":"FIRST_NAME","type":"private"},"date":1610819511,"text":"hi there"
                }
            },
            {
                "update_id":161176029,
                "message":{
                    "message_id":812,
                    "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
                    "chat":{"id":123456789,"first_name":"FIRST_NAME","type":"private"},"date":1610819511,"text":"how are you?"
                }
            }
            ]
        }
    return multiple_messages

@pytest.fixture
def input_single_message():
    single_message = {
        "update_id":161176028,
        "message":{
            "message_id":811,
            "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
            "chat":{"id":123456789,"first_name":"FIRST_NAME","type":"private"},"date":1610819511,"text":"hi there"
            }
        }
    return single_message

@pytest.fixture
def input_single_callback():
    single_callback = {
        "update_id":161176348, 
        "callback_query":{"id":"1785005944518206064",
            "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
            "message":{
                "message_id":1369,"from":
                {"id":987654321,"is_bot":True,"first_name":"TEST_BOT_NAME","username":"TEST_BOT"},
                "chat":{"id":123456789,"first_name":"FIRST_NAME","type":"private"},
                "date":1639921259,"text":"Alternative A oder B?",
                "reply_markup":{"inline_keyboard":[[{"text":"A","callback_data":"A"},{"text":"B","callback_data":"B"}]]}
                }
            ,"chat_instance":"630986056078679937","data":"B"
            }
        }
    return single_callback

@pytest.fixture
def input_single_group_chat_created():
    group_chat_created = {
            "update_id":161176351,
            "message":{
                "message_id":1373,
                "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
                "chat":{"id":-661875399,"title":"NAME_OF_GROUP","type":"group","all_members_are_administrators":True},
                "date":1650264798,"group_chat_created":True}
        }
    return group_chat_created

@pytest.fixture
def input_single_my_chat_member():
    my_chat_member = {
        "update_id":161176350,
        "my_chat_member":{
            "chat":{"id":-661875399,"title":"NAME_OF_GROUP","type":"group","all_members_are_administrators":False},
            "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
            "date":1650264798,
            "old_chat_member":{
                "user":{"id":987654321,"is_bot":True,"first_name":"TEST_NAME","username":"TEST_BOT"},"status":"left"},
            "new_chat_member":{
                "user":{"id":987654321,"is_bot":True,"first_name":"TEST_NAME","username":"TEST_BOT"},"status":"member"}
            }
        }
    return my_chat_member
        
@pytest.fixture
def input_single_jpeg():
    single_jpeg = {
        "update_id":161176352,
        "message":{
            "message_id":1374,
            "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
            "chat":{"id":123456789,"first_name":"FIRST_NAME","type":"private"},
            "date":1650267846,
            "photo":[
                {"file_id":"ABCDEfghi","file_unique_id":"aSKLJ21","file_size":1550,"width":90,"height":86},
                {"file_id":"ABDCFeghi","file_unique_id":"akSlJ21","file_size":10727,"width":320,"height":305},
                {"file_id":"adcbFEIHG","file_unique_id":"21jlSKA","file_size":29738,"width":800,"height":762},
                {"file_id":"abcDEfhig","file_unique_id":"2jlska1","file_size":55267,"width":1280,"height":1220}
            ], 
            "caption": "this is a jpeg"
        }
    }
    return single_jpeg

@pytest.fixture
def input_single_pdf():
    single_pdf = {
        "update_id":161176353,
        "message":{
            "message_id":1375,
            "from":{"id":123456789,"is_bot":False,"first_name":"FIRST_NAME","language_code":"en"},
            "chat":{"id":123456789,"first_name":"FIRST_NAME","type":"private"},
            "date":1650268239,
            "document":{"file_name":"FILE_NAME.pdf","mime_type":"application/pdf",
                "file_id":"FILE_ID","file_unique_id":"UNIQUE_ID","file_size":172104
            }
        }
    }
    return single_pdf


def test_telegram_listener__get_incoming_message_and_next_update_id_with_incoming_messages(input_multiple_messages, input_single_message):
    assert tl._get_incoming_message_and_next_update_id(input_multiple_messages) == (input_single_message, 161176029)

def test_telegram_listener__get_incoming_message_and_next_update_id_without_incoming_messages(no_incoming_messages):
    assert tl._get_incoming_message_and_next_update_id(no_incoming_messages) == (None, None)

def test_telegram_listener__set_extraction_method_with_message(input_single_message):
    assert tl._set_extraction_method(input_single_message) == "extract_message"

def test_telegram_listener__set_extraction_method_with_callback(input_single_callback):
    assert tl._set_extraction_method(input_single_callback) == "extract_callback"

def test_telegram_listener__set_extraction_method_with_group_chat_created(input_single_group_chat_created):
    assert tl._set_extraction_method(input_single_group_chat_created) == "do_not_extract"

def test_telegram_listener__set_extraction_method_with_my_chat_member_message(input_single_my_chat_member):
    assert tl._set_extraction_method(input_single_my_chat_member) == "do_not_extract"

def test_telegram_listener__extract_message_with_message(input_single_message):
    assert tl._extract_message(input_single_message) == (123456789, 161176028, "hi there", '2021-01-16 18:51:51')

def test_telegram_listener__extract_message_with_jpeg(input_single_jpeg):
    assert tl._extract_message(input_single_jpeg) == (123456789, 161176352, 'file: abcDEfhig', '2022-04-18 09:44:06')

def test_telegram_listener__extract_message_with_pdf(input_single_pdf):
    assert tl._extract_message(input_single_pdf) == (123456789, 161176353, 'file: FILE_ID', '2022-04-18 09:50:39')

def test_telegram_listener__extract_callback(input_single_callback):
    assert tl._extract_callback(input_single_callback) == (123456789, 161176348, 'B', '2021-12-19 14:40:59')
