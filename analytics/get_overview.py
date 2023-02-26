"""
Get total hours fasted for group
"""

from utils import db_conn


def load_fasting_hours(OBSERVATION_PERIOD_IN_DAYS):
    """
    Get total hours fasted in observation period.
    :return: total hours fasted
    :rtype: float
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
