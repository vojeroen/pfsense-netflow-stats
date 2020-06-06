import datetime

import pytz


def ms_to_ts(ms):
    return pytz.utc.localize(datetime.datetime.utcfromtimestamp(ms / 1000))


def ts_to_ms(ts):
    return int(
        (ts - pytz.utc.localize(datetime.datetime(1970, 1, 1))).total_seconds() * 1000
    )


def to_minute_start(ts):
    ts = ts.astimezone(pytz.utc)
    return pytz.utc.localize(
        datetime.datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, 0)
    )


def to_minute_end(ts):
    ts = ts.astimezone(pytz.utc) + datetime.timedelta(seconds=60)
    return pytz.utc.localize(
        datetime.datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, 0)
    )


def to_hour_start(ts):
    ts = ts.astimezone(pytz.utc)
    return pytz.utc.localize(
        datetime.datetime(ts.year, ts.month, ts.day, ts.hour, 0, 0)
    )


def to_hour_end(ts):
    ts = ts.astimezone(pytz.utc) + datetime.timedelta(seconds=3600)
    return pytz.utc.localize(
        datetime.datetime(ts.year, ts.month, ts.day, ts.hour, 0, 0)
    )


def to_day_start(ts):
    ts = ts.astimezone(pytz.utc)
    return pytz.utc.localize(datetime.datetime(ts.year, ts.month, ts.day, 0, 0, 0))


def to_day_end(ts):
    ts = ts.astimezone(pytz.utc) + datetime.timedelta(days=1)
    return pytz.utc.localize(datetime.datetime(ts.year, ts.month, ts.day, 0, 0, 0))


def now_ms():
    return ts_to_ms(pytz.utc.localize(datetime.datetime.utcnow()))
