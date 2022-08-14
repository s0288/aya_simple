from urllib.parse import urlparse
import os
import psycopg2
from datetime import datetime, timedelta
import pytz

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


URL = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_TOKEN')}/"

DB = os.environ.get("DB")
RESULT = urlparse(DB)
USERNAME = RESULT.username
PASSWORD = RESULT.password
DATABASE = RESULT.path[1:]
HOSTNAME = RESULT.hostname
PORT = RESULT.port


def db_conn():
    """Connect to db"""
    conn = psycopg2.connect(
        database=DATABASE, user=USERNAME, password=PASSWORD, host=HOSTNAME, port=PORT
    )
    return conn


def load_users():
    """
    get the most recent telegram_id-name combination for each telegram_id
    :return: telegram_id-name combination of users
    :rtype: dict
    """
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select
                    u.telegram_id, u.name
                from {os.environ.get('DB_PROD_LEVEL')}.users u
                join (
                        select telegram_id, max(status_timestamp) as max_timestamp
                        from {os.environ.get('DB_PROD_LEVEL')}.users group by telegram_id
                    ) s
                on
                    u.telegram_id = s.telegram_id
                    and u.status_timestamp = s.max_timestamp
                ;"""
            )
            df_users = cur.fetchall()
    return {row[0]: row[1] for row in df_users}


def write_user_to_db(telegram_id, name):
    """
    Write new users to database.
    :param telegram_id: Telegram ID of user
    :param name: name of user
    """
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {os.environ.get('DB_PROD_LEVEL')}.users
                    (telegram_id, name, status_timestamp)
                VALUES
                    ({telegram_id}, '{name}', '{datetime.now()}')
                """
            )


def write_msg_to_db(
    chat_id,
    telegram_id,
    message_text,
    timestamp_received,
    update_id=None,
    event_name=None,
):
    """
    Write msg to database.
    :param telegram_id: Telegram ID of user
    :param name: name of user
    """
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {os.environ.get('DB_PROD_LEVEL')}.aya_messages
                    (chat_id, telegram_id, update_id, message_text, event_name, timestamp_received, timestamp_saved)
                VALUES
                    (
                        %s, %s, %s, %s, %s, %s, %s
                    )""",
                (
                    chat_id,
                    telegram_id,
                    update_id,
                    message_text,
                    event_name,
                    timestamp_received,
                    datetime.now(),
                ),
            )


def convert_secs_to_datetime(secs):
    return datetime.fromtimestamp(secs).strftime("%Y-%m-%d %H:%M:%S")


def get_time_since_fasting_start(telegram_id):
    """
    Get time since the user started to fast. If the user doesn't fast, return None.
    :param telegram_id: Telegram ID of user
    :return: time since start of fast
    :rtype: str
    """
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                select
                    max_start
                from (
                select
                    max(timestamp_received) filter(where event_name='fast_start') as max_start,
                    max(timestamp_received) filter(where event_name='fast_end') as max_end
                from {os.environ.get('DB_PROD_LEVEL')}.aya_messages
                where chat_id = {telegram_id}
                ) sub
                where max_start > coalesce(max_end, '2001-01-01 00:00:00');
                """
            )
            try:
                time_at_fasting_start = cur.fetchall()[0][0]
                hours_as_float, hours_as_text = _get_time_since_fasting_start(
                    time_at_fasting_start
                )
            except:
                hours_as_float, hours_as_text = None, None
    return hours_as_float, hours_as_text


def _get_time_since_fasting_start(time_at_fasting_start):
    seconds = (datetime.now() - time_at_fasting_start).total_seconds()
    hours_as_float = round(seconds / 60 / 60, 4)
    mins, _ = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    hours_as_text = f"{hours:,.0f} Stunden und {mins:,.0f} Minuten"
    return hours_as_float, hours_as_text


def write_event_to_db(telegram_id, event_name, event_value=None):
    """
    Write new event to SCHEMA.aya_events.
    :param telegram_id: Telegram ID of user
    :param event_name: name of event
    :param event_value: value of event
    """

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {os.environ.get('DB_PROD_LEVEL')}.aya_events
                    (chat_id, telegram_id, event_name, event_value, timestamp_saved)
                VALUES
                    (%s, %s, %s, %s, %s)""",
                (telegram_id, telegram_id, event_name, event_value, datetime.now()),
            )
