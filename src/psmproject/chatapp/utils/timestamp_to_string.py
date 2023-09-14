from datetime import datetime as dt
from datetime import timedelta


def timestamp_to_str(timestamp):
    today = dt.today().date()
    if today == timestamp.date():
        return timestamp.strftime("Today, %H:%M:%S")
    if today - timedelta(days=7) <= timestamp.date():
        return timestamp.strftime("%A, %H:%M:%S")
    return timestamp.strftime("%d %B %Y, %H:%M:%S")
