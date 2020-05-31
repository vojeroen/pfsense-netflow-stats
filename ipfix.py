import logging
import uuid

from netflow.collector import get_export_packets

from models import Session
from models.export_packet import ExportPacket, Client, Header, Flow

HOST = "0.0.0.0"
PORT = 9000

session = Session()

for ts, client, export in get_export_packets(HOST, PORT):
    export_packet = ExportPacket(id=uuid.uuid4().hex, timestamp=ts * 1000)
    session.add(export_packet)

    client = Client(
        id=uuid.uuid4().hex, export_packet=export_packet, host=client[0], port=client[1]
    )
    session.add(client)

    try:
        header = Header(
            id=uuid.uuid4().hex, export_packet=export_packet, **export.header.to_dict()
        )
    except TypeError as e:
        logging.error("Error creating header: " + str(e))
        session.rollback()
        continue
    session.add(header)

    for flow_data in (f.data for f in export.flows):
        try:
            flow = Flow(id=uuid.uuid4().hex, export_packet=export_packet, **flow_data)
        except TypeError as e:
            logging.error("Error creating flow: " + str(e))
            continue
        session.add(flow)

    try:
        session.commit()
    except Exception as e:
        logging.error("Commit failed: " + str(e))
        session.rollback()
