import sys


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
