import sys
from datetime import datetime as dt

from django.utils import timezone as tz


def receiver_not_in_test(signal, **kwargs):
    """
    Special version of django receiver decorator for connecting signals only when running NOT in django tests.
    Extends functionality of: django.dispatch.receiver
    """

    def _decorator(func):
        if "test" in sys.argv:
            return func
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func

    return _decorator


times = {"start": dt.min.time(), "end": dt.max.time()}


def get_tz_aware_date(original_datetime, time_type):
    return dt.combine(original_datetime, times[time_type], tzinfo=tz.get_current_timezone())
