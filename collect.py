import gzip
import json
import os
import uuid

from netflow.collector import get_export_packets

HOST = "0.0.0.0"
PORT = 9000

CACHE_DIR = "cache/"

for ts, client, export in get_export_packets(HOST, PORT):
    with gzip.open(os.path.join(CACHE_DIR, uuid.uuid4().hex + ".gz"), "wb") as ofile:
        ofile.write(
            json.dumps(
                {
                    "ts": ts,
                    "client": client,
                    "header": export.header.to_dict(),
                    "flows": [f.data for f in export.flows],
                }
            ).encode()
        )
