from sqlalchemy import Column, BigInteger, ForeignKey, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models import Base


class ExportPacket(Base):
    __tablename__ = "export_packet"

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False,)
    timestamp = Column(BigInteger, unique=False, nullable=False)

    client = relationship("Client", uselist=False, back_populates="export_packet")
    header = relationship("Header", uselist=False, back_populates="export_packet")
    flows = relationship("Flow", back_populates="export_packet")


class Client(Base):
    __tablename__ = "client"

    export_packet_id = Column(UUID, ForeignKey("export_packet.id"))
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False,)
    host = Column(String, unique=False, nullable=False)
    port = Column(Integer, unique=False, nullable=False)

    export_packet = relationship("ExportPacket", back_populates="client")


class Header(Base):
    __tablename__ = "header"

    export_packet_id = Column(UUID, ForeignKey("export_packet.id"))
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False,)
    version = Column(Integer, unique=False, nullable=False)
    length = Column(Integer, unique=False, nullable=False)
    export_uptime = Column(Integer, unique=False, nullable=False)
    sequence_number = Column(Integer, unique=False, nullable=False)
    obervation_domain_id = Column(Integer, unique=False, nullable=False)

    export_packet = relationship("ExportPacket", back_populates="header")


class Flow(Base):
    __tablename__ = "flow"

    export_packet_id = Column(UUID, ForeignKey("export_packet.id"))
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False,)

    protocolIdentifier = Column(Integer, unique=False, nullable=True)
    vlanId = Column(Integer, unique=False, nullable=True)
    postVlanId = Column(Integer, unique=False, nullable=True)
    ingressInterface = Column(Integer, unique=False, nullable=True)
    egressInterface = Column(Integer, unique=False, nullable=True)

    flowStartMilliseconds = Column(BigInteger, unique=False, nullable=True)
    flowEndMilliseconds = Column(BigInteger, unique=False, nullable=True)

    ipVersion = Column(Integer, unique=False, nullable=True)
    ipClassOfService = Column(Integer, unique=False, nullable=True)

    sourceMacAddress = Column(String, unique=False, nullable=True)
    sourceIPv4Address = Column(String, unique=False, nullable=True)
    sourceIPv6Address = Column(String, unique=False, nullable=True)
    sourceTransportPort = Column(Integer, unique=False, nullable=True)

    destinationMacAddress = Column(String, unique=False, nullable=True)
    postDestinationMacAddress = Column(String, unique=False, nullable=True)
    destinationIPv4Address = Column(String, unique=False, nullable=True)
    destinationIPv6Address = Column(String, unique=False, nullable=True)
    destinationTransportPort = Column(Integer, unique=False, nullable=True)

    octetDeltaCount = Column(Integer, unique=False, nullable=True)
    packetDeltaCount = Column(Integer, unique=False, nullable=True)

    icmpTypeCodeIPv4 = Column(Integer, unique=False, nullable=True)
    icmpTypeCodeIPv6 = Column(Integer, unique=False, nullable=True)

    tcpControlBits = Column(Integer, unique=False, nullable=True)
    samplingPacketSpace = Column(Integer, unique=False, nullable=True)
    samplingPacketInterval = Column(Integer, unique=False, nullable=True)
    selectorAlgorithm = Column(Integer, unique=False, nullable=True)
    systemInitTimeMilliseconds = Column(BigInteger, unique=False, nullable=True)
    meteringProcessId = Column(BigInteger, unique=False, nullable=True)

    export_packet = relationship("ExportPacket", back_populates="flows")
