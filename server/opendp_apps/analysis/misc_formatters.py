from datetime import datetime as dt


def get_timestamp_str(dt_obj: dt = None) -> str:
    """Get a timestamp as part of a filename"""
    if not dt_obj:
        dt_obj = dt.now()

    str_pattern = '%Y-%m-%d_%H-%M-%S'
    return dt_obj.strftime(str_pattern)


def get_readable_datetime(dt_obj: dt) -> str:
    """
    Format a datetime object
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    """
    tz_str = dt_obj.strftime("%Z")
    if tz_str:
        tz_str = f'{tz_str}'

    readable_str = (f'{dt_obj.strftime("%B")} {dt_obj.strftime("%-d")}, {dt_obj.strftime("%Y")}'
                    f' at {dt_obj.strftime("%H:%M:%S:%f")} {tz_str}')

    return readable_str
