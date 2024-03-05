from datetime import datetime as dt

from django.utils import timezone as tz

times = {"start": dt.min.time(), "end": dt.max.time()}


def get_tz_aware_date(original_datetime, time_type):
    return dt.combine(original_datetime, times[time_type], tzinfo=tz.get_current_timezone())
