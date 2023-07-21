from datetime import datetime, timedelta
from django.utils.timezone import make_aware

_CURR_YYYY_MMDD = None


def get_yyyy_mmdd():
    """YYYY_MMDD - e.g. '2020_0104', or similar"""
    global _CURR_YYYY_MMDD

    if not _CURR_YYYY_MMDD:
        dt_now = datetime.now()
        _CURR_YYYY_MMDD = '%s_%s%s' % (dt_now.year,
                                       str(dt_now.month).zfill(2),
                                       str(dt_now.day).zfill(2),)

    return _CURR_YYYY_MMDD


def get_expiration_date(days=5, microseconds=0):
    """Get the expiration date for an analysis plan"""
    return make_aware(datetime.now() + timedelta(days=days, microseconds=microseconds))

def get_expiration_date_str(days=5):
    """Get the expiration date for an analysis plan"""
    return get_expiration_date(days).strftime('%Y-%m-%d')
