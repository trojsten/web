from datetime import datetime

def is_true(value):
    """Converts GET parameter value to bool
    """
    return bool(value) and value.lower() not in ('false', '0')


def default_start_time():
    return datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def default_end_time():
    return datetime.now().replace(
        hour=23, minute=59, second=59, microsecond=0
    )
