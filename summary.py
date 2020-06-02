import uuid

from sqlalchemy import func

from models import Session
from models.export_packet import ParsedExportPacket
from models.summary import SummaryUpdateTime, SummaryMinute

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

# prepare insert statements
insert_summary_minute = SummaryMinute.__table__.insert().from_select(
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

# remove existing data
session.query(SummaryMinute).filter(
    SummaryMinute.unix_start_ms >= min_unix_start_ms
).filter(SummaryMinute.unix_start_ms <= max_unix_start_ms).delete()

# insert new data
session.execute(insert_summary_minute)

# store last updated timestamp
session.query(SummaryUpdateTime).delete()
session.add(
    SummaryUpdateTime(id=uuid.uuid4().hex, last_unix_updated_ms=max_unix_updated_ms)
)

# commit
session.commit()
