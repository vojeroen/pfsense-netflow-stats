import datetime
import uuid

import pandas
import pytz
from sqlalchemy import func

from helpers.time import (
    ts_to_ms,
    to_hour_start,
    ms_to_ts,
    to_hour_end,
    to_day_start,
    to_day_end,
)
from models import Session
from models.export_packet import ParsedExportPacket
from models.summary import SummaryUpdateTime, SummaryMinute, SummaryHour, SummaryDay

session = Session()

# identify what needs to be updated
min_unix_updated_ms = session.query(SummaryUpdateTime.last_unix_updated_ms).first()
try:
    min_unix_updated_ms = min_unix_updated_ms[0]
except TypeError:
    min_unix_updated_ms = 0

min_unix_start_ms, max_unix_start_ms, max_unix_updated_ms = (
    session.query(
        func.min(ParsedExportPacket.unix_start_ms),
        func.max(ParsedExportPacket.unix_start_ms),
        func.max(ParsedExportPacket.unix_updated_ms),
    )
    .filter(ParsedExportPacket.unix_updated_ms > min_unix_updated_ms)
    .first()
)
if not min_unix_start_ms:
    min_unix_start_ms = 0
if not max_unix_start_ms:
    max_unix_start_ms = 0
if not max_unix_updated_ms:
    max_unix_updated_ms = min_unix_updated_ms


# remove existing minute data
session.query(SummaryMinute).filter(
    SummaryMinute.unix_start_ms >= min_unix_start_ms
).filter(SummaryMinute.unix_start_ms <= max_unix_start_ms).delete()


# insert new minute data
session.execute(
    SummaryMinute.__table__.insert().from_select(
        [
            SummaryMinute.id,
            SummaryMinute.unix_start_ms,
            SummaryMinute.unix_end_ms,
            SummaryMinute.year,
            SummaryMinute.month,
            SummaryMinute.day,
            SummaryMinute.hour,
            SummaryMinute.minute,
            SummaryMinute.offset,
            SummaryMinute.ip_version,
            SummaryMinute.protocol,
            SummaryMinute.local_address,
            SummaryMinute.local_name,
            SummaryMinute.remote_address,
            SummaryMinute.remote_name,
            SummaryMinute.port,
            SummaryMinute.direction,
            SummaryMinute.connections,
            SummaryMinute.packets,
            SummaryMinute.octets,
        ],
        session.query(
            func.uuid_generate_v4(),
            ParsedExportPacket.unix_start_ms,
            ParsedExportPacket.unix_end_ms,
            ParsedExportPacket.year,
            ParsedExportPacket.month,
            ParsedExportPacket.day,
            ParsedExportPacket.hour,
            ParsedExportPacket.minute,
            ParsedExportPacket.offset,
            ParsedExportPacket.ip_version,
            ParsedExportPacket.protocol,
            ParsedExportPacket.local_address,
            ParsedExportPacket.local_name,
            ParsedExportPacket.remote_address,
            ParsedExportPacket.remote_name,
            ParsedExportPacket.port,
            ParsedExportPacket.direction,
            func.sum(ParsedExportPacket.connections).label("connections"),
            func.sum(ParsedExportPacket.packets).label("packets"),
            func.sum(ParsedExportPacket.octets).label("octets"),
        )
        .filter(ParsedExportPacket.unix_start_ms >= min_unix_start_ms)
        .filter(ParsedExportPacket.unix_start_ms <= max_unix_start_ms)
        .group_by(
            ParsedExportPacket.unix_start_ms,
            ParsedExportPacket.unix_end_ms,
            ParsedExportPacket.year,
            ParsedExportPacket.month,
            ParsedExportPacket.day,
            ParsedExportPacket.hour,
            ParsedExportPacket.minute,
            ParsedExportPacket.offset,
            ParsedExportPacket.ip_version,
            ParsedExportPacket.protocol,
            ParsedExportPacket.local_address,
            ParsedExportPacket.local_name,
            ParsedExportPacket.remote_address,
            ParsedExportPacket.remote_name,
            ParsedExportPacket.port,
            ParsedExportPacket.direction,
        ),
    )
)


# prepare parameters for hour summary
hour_min_unix_start_ms = ts_to_ms(to_hour_start(ms_to_ts(min_unix_start_ms)))
hour_max_unix_start_ms = ts_to_ms(to_hour_end(ms_to_ts(max_unix_start_ms))) - 1

# remove existing hour data
session.query(SummaryHour).filter(
    SummaryHour.unix_start_ms >= hour_min_unix_start_ms
).filter(SummaryHour.unix_start_ms <= hour_max_unix_start_ms).delete()

# insert new hour data
hour_data = pandas.read_sql(
    session.query(
        func.uuid_generate_v4().label("id"),
        SummaryMinute.year,
        SummaryMinute.month,
        SummaryMinute.day,
        SummaryMinute.hour,
        SummaryMinute.offset,
        SummaryMinute.ip_version,
        SummaryMinute.protocol,
        SummaryMinute.local_address,
        SummaryMinute.local_name,
        SummaryMinute.remote_address,
        SummaryMinute.remote_name,
        SummaryMinute.port,
        SummaryMinute.direction,
        func.sum(SummaryMinute.connections).label("connections"),
        func.sum(SummaryMinute.packets).label("packets"),
        func.sum(SummaryMinute.octets).label("octets"),
    )
    .filter(SummaryMinute.unix_start_ms >= hour_min_unix_start_ms)
    .filter(SummaryMinute.unix_start_ms <= hour_max_unix_start_ms)
    .group_by(
        SummaryMinute.year,
        SummaryMinute.month,
        SummaryMinute.day,
        SummaryMinute.hour,
        SummaryMinute.offset,
        SummaryMinute.ip_version,
        SummaryMinute.protocol,
        SummaryMinute.local_address,
        SummaryMinute.local_name,
        SummaryMinute.remote_address,
        SummaryMinute.remote_name,
        SummaryMinute.port,
        SummaryMinute.direction,
    )
    .statement,
    session.bind,
)

if len(hour_data) > 0:
    hour_data.loc[:, "unix_start_ms"] = hour_data.loc[
        :, ["year", "month", "day", "hour", "offset"]
    ].apply(
        lambda r: ts_to_ms(
            pytz.utc.localize(
                datetime.datetime(r["year"], r["month"], r["day"], r["hour"], 0, 0)
                - datetime.timedelta(seconds=int(r["offset"]))
            )
        ),
        axis="columns",
    )

    hour_data["unix_end_ms"] = hour_data["unix_start_ms"] + 3600 * 1000

    hour_data = hour_data.set_index("unix_start_ms")


# # prepare parameters for day summary
# day_min_ts = to_day_start(ms_to_ts(min_unix_start_ms)).date()
# day_max_ts = to_day_end(ms_to_ts(max_unix_start_ms)).date()
#
# # remove existing day data
# session.query(SummaryDay).filter(SummaryDay.date >= day_min_ts).filter(
#     SummaryDay.date <= day_max_ts
# ).delete()
#
# # insert new day data
# session.execute(
#     SummaryDay.__table__.insert().from_select(
#         [
#             SummaryDay.id,
#             SummaryDay.date,
#             SummaryDay.year,
#             SummaryDay.month,
#             SummaryDay.day,
#             SummaryDay.ip_version,
#             SummaryDay.protocol,
#             SummaryDay.local_address,
#             SummaryDay.local_name,
#             SummaryDay.remote_address,
#             SummaryDay.remote_name,
#             SummaryDay.port,
#             SummaryDay.direction,
#             SummaryDay.connections,
#             SummaryDay.packets,
#             SummaryDay.octets,
#         ],
#         session.query(
#             func.uuid_generate_v4(),
#             func.to_date(
#                 SummaryMinute.year + SummaryMinute.month + SummaryMinute.day, "YYYYMMDD"
#             ),
#             SummaryMinute.year,
#             SummaryMinute.month,
#             SummaryMinute.day,
#             SummaryMinute.ip_version,
#             SummaryMinute.protocol,
#             SummaryMinute.local_address,
#             SummaryMinute.local_name,
#             SummaryMinute.remote_address,
#             SummaryMinute.remote_name,
#             SummaryMinute.port,
#             SummaryMinute.direction,
#             func.sum(SummaryMinute.connections).label("connections"),
#             func.sum(SummaryMinute.packets).label("packets"),
#             func.sum(SummaryMinute.octets).label("octets"),
#         )
#         .filter(
#             func.date(SummaryMinute.year, SummaryMinute.month, SummaryMinute.day)
#             >= day_min_ts
#         )
#         .filter(
#             func.date(SummaryMinute.year, SummaryMinute.month, SummaryMinute.day)
#             <= day_max_ts
#         )
#         .group_by(
#             SummaryMinute.year,
#             SummaryMinute.month,
#             SummaryMinute.day,
#             SummaryMinute.ip_version,
#             SummaryMinute.protocol,
#             SummaryMinute.local_address,
#             SummaryMinute.local_name,
#             SummaryMinute.remote_address,
#             SummaryMinute.remote_name,
#             SummaryMinute.port,
#             SummaryMinute.direction,
#         ),
#     )
# )

# store last updated timestamp
session.query(SummaryUpdateTime).delete()
session.add(
    SummaryUpdateTime(id=uuid.uuid4().hex, last_unix_updated_ms=max_unix_updated_ms)
)

# commit
session.commit()

# write hour data
if len(hour_data) > 0:
    hour_data.to_sql(SummaryHour.__tablename__, session.bind, if_exists="append")
