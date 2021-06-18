from datetime import datetime

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

def dashes():
    print('-' * 40)

def msgt(m):
    dashes()
    print(m)
    dashes()
