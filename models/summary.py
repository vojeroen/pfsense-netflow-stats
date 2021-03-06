from sqlalchemy import Column, String, Integer, Numeric, BigInteger, Date
from sqlalchemy.dialects.postgresql import UUID

from models import Base


class SummaryUpdateTime(Base):
    __tablename__ = "summary_update_time"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    last_unix_updated_ms = Column(BigInteger, unique=False, nullable=True)


class SummaryMinute(Base):
    __tablename__ = "summary_minute"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)

    unix_start_ms = Column(BigInteger, unique=False, nullable=False)
    unix_end_ms = Column(BigInteger, unique=False, nullable=False)

    year = Column(Integer, unique=False, nullable=False)
    month = Column(Integer, unique=False, nullable=False)
    day = Column(Integer, unique=False, nullable=False)
    hour = Column(Integer, unique=False, nullable=False)
    minute = Column(Integer, unique=False, nullable=False)
    offset = Column(Integer, unique=False, nullable=False)

    ip_version = Column(Integer, unique=False, nullable=False)
    protocol = Column(String, unique=False, nullable=False)

    local_address = Column(String, unique=False, nullable=False)
    local_name = Column(String, unique=False, nullable=True)

    remote_address = Column(String, unique=False, nullable=False)
    remote_name = Column(String, unique=False, nullable=True)

    port = Column(Integer, unique=False, nullable=False)
    direction = Column(String, unique=False, nullable=False)

    connections = Column(Numeric, unique=False, nullable=False)
    packets = Column(Numeric, unique=False, nullable=False)
    octets = Column(Numeric, unique=False, nullable=False)


class SummaryHour(Base):
    __tablename__ = "summary_hour"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)

    unix_start_ms = Column(BigInteger, unique=False, nullable=False)
    unix_end_ms = Column(BigInteger, unique=False, nullable=False)

    year = Column(Integer, unique=False, nullable=False)
    month = Column(Integer, unique=False, nullable=False)
    day = Column(Integer, unique=False, nullable=False)
    hour = Column(Integer, unique=False, nullable=False)
    offset = Column(Integer, unique=False, nullable=False)

    ip_version = Column(Integer, unique=False, nullable=False)
    protocol = Column(String, unique=False, nullable=False)

    local_address = Column(String, unique=False, nullable=False)
    local_name = Column(String, unique=False, nullable=True)

    remote_address = Column(String, unique=False, nullable=False)
    remote_name = Column(String, unique=False, nullable=True)

    port = Column(Integer, unique=False, nullable=False)
    direction = Column(String, unique=False, nullable=False)

    connections = Column(Numeric, unique=False, nullable=False)
    packets = Column(Numeric, unique=False, nullable=False)
    octets = Column(Numeric, unique=False, nullable=False)


class SummaryDay(Base):
    __tablename__ = "summary_day"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)

    date = Column(Date, unique=False, nullable=False)

    year = Column(Integer, unique=False, nullable=False)
    month = Column(Integer, unique=False, nullable=False)
    day = Column(Integer, unique=False, nullable=False)

    ip_version = Column(Integer, unique=False, nullable=False)
    protocol = Column(String, unique=False, nullable=False)

    local_address = Column(String, unique=False, nullable=False)
    local_name = Column(String, unique=False, nullable=True)

    remote_address = Column(String, unique=False, nullable=False)
    remote_name = Column(String, unique=False, nullable=True)

    port = Column(Integer, unique=False, nullable=False)
    direction = Column(String, unique=False, nullable=False)

    connections = Column(Numeric, unique=False, nullable=False)
    packets = Column(Numeric, unique=False, nullable=False)
    octets = Column(Numeric, unique=False, nullable=False)
