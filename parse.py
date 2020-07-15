import datetime
import gzip
import ipaddress
import json
import logging
import os
import shutil
import time
import uuid
from json.decoder import JSONDecodeError
from pprint import pprint

import pandas
import pytz
from cachetools import cached, TTLCache

from helpers.dns import get_domain_name
from helpers.time import ms_to_ts, ts_to_ms, to_minute_start, to_minute_end
from models import Session
from models.export_packet import ParsedExportPacket

logging.basicConfig(level=logging.DEBUG)

# constants
EPHEMERAL_PORT_RANGE_START = 32768
EPHEMERAL_PORT_RANGE_END = 65535

PROTOCOL_MAP = {
    # https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}

LOCAL_ADDRESS = [192, 168, 42]
VPN_ADDRESS = [192, 168, 43]

PROCESS_ID = uuid.uuid4().hex

CACHE_DIR = "cache/"
PROCESSING_DIR = os.path.join(CACHE_DIR, "processing-" + PROCESS_ID)
PARSED_DIR = "parsed/"

IPFIX_TO_DB_MAP = {
    "id": "id",
    "intervalStart": "unix_start_ms",
    "intervalEnd": "unix_end_ms",
    "year": "year",
    "month": "month",
    "day": "day",
    "hour": "hour",
    "minute": "minute",
    "offset": "offset",
    "ipVersion": "ip_version",
    "protocolIdentifier": "protocol",
    "localAddress": "local_address",
    "localName": "local_name",
    "remoteAddress": "remote_address",
    "remoteName": "remote_name",
    "port": "port",
    "direction": "direction",
    "connections": "connections",
    "packets": "packets",
    "octets": "octets",
}


# transformation helper functions
@cached(cache=TTLCache(maxsize=1024 * 1024, ttl=900))
def convert_decimal_ip_address_to_string(ip):
    if ip is None:
        return ip
    try:
        ip = int(ip)
    except (TypeError, ValueError):
        logging.error("Cannot parse IP address: " + str(ip))
        return ip
    return str(ipaddress.ip_address(ip))


def return_local_and_remote_address(row):
    if row["ipVersion"] == 4:
        split_source_address = [int(i) for i in row["sourceAddress"].split(".")]
        split_destination_address = [
            int(i) for i in row["destinationAddress"].split(".")
        ]
        source_is_local = (
            (split_source_address[: len(LOCAL_ADDRESS)] == LOCAL_ADDRESS)
            or (split_source_address[: len(VPN_ADDRESS)] == VPN_ADDRESS)
            or (split_source_address == [0, 0, 0, 0])
        )
        destination_is_local = (
            (split_destination_address[: len(LOCAL_ADDRESS)] == LOCAL_ADDRESS)
            or (split_destination_address[: len(VPN_ADDRESS)] == VPN_ADDRESS)
            or (split_destination_address == [0, 0, 0, 0])
        )
        if source_is_local and destination_is_local:
            return row["sourceAddress"], row["destinationAddress"], "internal"
        elif source_is_local:
            return row["sourceAddress"], row["destinationAddress"], "upload"
        elif destination_is_local:
            return row["destinationAddress"], row["sourceAddress"], "download"
        else:
            logging.error(
                "Cannot find local address, "
                "keeping source as local and destination as remote: " + str(row)
            )
            return row["sourceAddress"], row["destinationAddress"], "unknown"
    elif row["ipVersion"] == 6:
        # TODO: make this more accurate
        logging.warning(
            "IPv6 has no local address detection yet, "
            "keeping source as local and destination as remote: " + str(row)
        )
        return row["sourceAddress"], row["destinationAddress"], "unknown"


@cached(cache=TTLCache(maxsize=1024 * 1024, ttl=900))
def convert_decimal_mac_address_to_string(mac):
    try:
        mac = int(mac)
    except (TypeError, ValueError):
        return mac
    mac = format(mac, "x")
    try:
        return ":".join(format(s, "02x") for s in bytes.fromhex(mac))
    except ValueError:
        return ":".join(format(s, "02x") for s in bytes.fromhex("0" + mac))


def convert_ephemeral_ports(port):
    try:
        port = int(port)
    except (TypeError, ValueError):
        return port
    if EPHEMERAL_PORT_RANGE_START <= port <= EPHEMERAL_PORT_RANGE_END:
        return 0
    else:
        return port


def set_main_port(row):
    if row["sourceTransportPort"] == 0:
        return row["destinationTransportPort"]
    elif row["destinationTransportPort"] == 0:
        return row["sourceTransportPort"]
    else:
        return min(row["sourceTransportPort"], row["destinationTransportPort"])


def convert_protocol(protocol):
    try:
        return PROTOCOL_MAP[protocol]
    except KeyError:
        return "UNKNOWN"


def calculate_interval(ms_start, ms_end):
    interval_start = [ts_to_ms(to_minute_start(ms_to_ts(ms_start)))]
    interval_end = ts_to_ms(to_minute_end(ms_to_ts(ms_start)))
    while interval_end < ms_end:
        interval_start.append(interval_start[-1] + 60 * 1000)
        interval_end += 60 * 1000
    return interval_start


# process_message function
def process_message(message):
    flows = []

    # filter and add intervals
    for flow in message["flows"]:
        if "ipVersion" not in flow.keys():
            continue
        flow["intervalStart"] = calculate_interval(
            flow["flowStartMilliseconds"], flow["flowEndMilliseconds"]
        )
        flows.append(flow)

    pprint(flows)

    # convert to dataframe
    flows = pandas.DataFrame(flows)

    if len(flows) == 0:
        return

    logging.info(
        "[{time}] Parsing: processing {flows} flows".format(
            time=pytz.utc.localize(datetime.datetime.utcnow()).isoformat(),
            flows=len(flows),
        )
    )

    # convert decimal IP addresses to strings
    ip_address_columns = [
        "sourceIPv4Address",
        "destinationIPv4Address",
        "sourceIPv6Address",
        "destinationIPv6Address",
    ]
    for col in ip_address_columns:
        try:
            flows[col] = flows[col].apply(convert_decimal_ip_address_to_string)
        except KeyError:
            flows[col] = None

    # set source and destination address
    flows["sourceAddress"] = flows["sourceIPv4Address"].fillna(
        flows["sourceIPv6Address"]
    )
    flows["destinationAddress"] = flows["destinationIPv4Address"].fillna(
        flows["destinationIPv6Address"]
    )

    # set local and remote address
    flows["localAddress"] = None
    flows["remoteAddress"] = None
    flows["direction"] = None
    flows.loc[:, ["localAddress", "remoteAddress", "direction"]] = (
        flows.loc[:, ["ipVersion", "sourceAddress", "destinationAddress"]]
        .apply(return_local_and_remote_address, axis="columns", result_type="expand")
        .rename(columns={0: "localAddress", 1: "remoteAddress", 2: "direction"})
    )

    # add DNS
    flows["localName"] = flows["localAddress"].apply(get_domain_name)
    flows["remoteName"] = flows["remoteAddress"].apply(get_domain_name)

    # convert decimal MAC addresses to strings
    mac_address_columns = [
        "sourceMacAddress",
        "destinationMacAddress",
        "postDestinationMacAddress",
    ]
    for col in mac_address_columns:
        try:
            flows[col] = flows[col].apply(convert_decimal_mac_address_to_string)
        except KeyError:
            flows[col] = None

    flows["destinationMacAddress"] = flows["destinationMacAddress"].fillna(
        flows["postDestinationMacAddress"]
    )

    # fill missing ports (e.g. ICMP)
    port_columns = [
        "sourceTransportPort",
        "destinationTransportPort",
    ]
    for col in port_columns:
        try:
            flows[col] = flows[col].fillna(0)
        except KeyError:
            flows[col] = 0

    # set main port
    flows["port"] = flows[["sourceTransportPort", "destinationTransportPort"]].apply(
        set_main_port, axis="columns"
    )

    # set readable protocol
    try:
        flows["protocolIdentifier"] = flows["protocolIdentifier"].apply(
            convert_protocol
        )
    except KeyError:
        flows["protocolIdentifier"] = convert_protocol(None)

    # explode intervals
    flows = flows.explode("intervalStart")
    flows["intervalEnd"] = flows["intervalStart"] + 60 * 1000

    # set start and end timestamps within the time window
    flows["timestampStart"] = flows["intervalStart"]
    flows["timestampStart"] = flows["timestampStart"].clip(
        lower=flows["flowStartMilliseconds"]
    )
    flows["timestampEnd"] = flows["intervalEnd"]
    flows["timestampEnd"] = flows["timestampEnd"].clip(
        upper=flows["flowEndMilliseconds"]
    )

    # calculate octets and packets within the time window
    # note: might be NaN if durationMilliseconds = 0, so we fill with the original value
    flows["durationMilliseconds"] = (
        flows["flowEndMilliseconds"] - flows["flowStartMilliseconds"]
    )
    flows["octets"] = (
        (flows["octetDeltaCount"] / flows["durationMilliseconds"])
        * (flows["timestampEnd"] - flows["timestampStart"])
    ).fillna(flows["octetDeltaCount"])
    flows["packets"] = (
        (flows["packetDeltaCount"] / flows["durationMilliseconds"])
        * (flows["timestampEnd"] - flows["timestampStart"])
    ).fillna(flows["packetDeltaCount"])
    flows["connections"] = 1

    # rounding
    flows["octets"] = flows["octets"].apply(lambda n: int(round(n, 0)))
    flows["packets"] = flows["packets"].apply(lambda n: int(round(n, 0)))

    # generate new id
    flows["id"] = None
    flows["id"] = flows["id"].apply(lambda u: uuid.uuid4().hex)
    flows = flows.set_index(["id"])

    # set timestamp info
    flows["year"] = flows["timestampStart"].apply(
        lambda t: ms_to_ts(t).astimezone(pytz.timezone("Europe/Brussels")).year
    )
    flows["month"] = flows["timestampStart"].apply(
        lambda t: ms_to_ts(t).astimezone(pytz.timezone("Europe/Brussels")).month
    )
    flows["day"] = flows["timestampStart"].apply(
        lambda t: ms_to_ts(t).astimezone(pytz.timezone("Europe/Brussels")).day
    )
    flows["hour"] = flows["timestampStart"].apply(
        lambda t: ms_to_ts(t).astimezone(pytz.timezone("Europe/Brussels")).hour
    )
    flows["minute"] = flows["timestampStart"].apply(
        lambda t: ms_to_ts(t).astimezone(pytz.timezone("Europe/Brussels")).minute
    )
    flows["offset"] = flows["timestampStart"].apply(
        lambda t: ms_to_ts(t)
        .astimezone(pytz.timezone("Europe/Brussels"))
        .utcoffset()
        .total_seconds()
    )

    # remove unnecessary columns
    flow_columns = set(flows.columns)
    for col in flow_columns.difference(IPFIX_TO_DB_MAP.keys()):
        del flows[col]
    flows.columns = [IPFIX_TO_DB_MAP[col] for col in flows.columns]

    return flows


# main function
def main():
    session = Session()

    while True:
        files = [
            f
            for f in os.listdir(CACHE_DIR)
            if os.path.isfile(os.path.join(CACHE_DIR, f))
        ]
        files = files[0:32]

        if len(files) > 0:
            now = datetime.datetime.utcnow()
            flows = pandas.DataFrame()

            for f in files[:]:
                src_dir = os.path.join(CACHE_DIR)
                prc_dir = os.path.join(PROCESSING_DIR)

                os.makedirs(prc_dir, exist_ok=True)
                try:
                    shutil.move(
                        os.path.join(src_dir, f), os.path.join(prc_dir, f),
                    )
                except FileNotFoundError:
                    files.remove(f)

            for f in files:
                prc_dir = os.path.join(PROCESSING_DIR)
                retry = 1
                while retry <= 10:
                    with gzip.open(os.path.join(prc_dir, f), "rb") as ifile:
                        try:
                            message = json.loads(ifile.read().decode())
                        except JSONDecodeError:
                            retry = retry + 1
                            time.sleep(0.1)
                        else:
                            flows = pandas.concat([flows, process_message(message)])
                            retry = 11

            if len(flows) > 0:
                logging.info("Storing parsed export packets to database")
                flows["unix_updated_ms"] = ts_to_ms(
                    pytz.utc.localize(datetime.datetime.utcnow())
                )
                flows.to_sql(
                    ParsedExportPacket.__tablename__, session.bind, if_exists="append"
                )

            for f in files:
                prc_dir = os.path.join(PROCESSING_DIR)
                dst_dir = os.path.join(
                    PARSED_DIR,
                    str(now.year).zfill(4),
                    str(now.month).zfill(2),
                    str(now.day).zfill(2),
                    str(now.hour).zfill(2),
                )

                os.makedirs(dst_dir, exist_ok=True)
                shutil.move(
                    os.path.join(prc_dir, f), os.path.join(dst_dir, f),
                )

            logging.info("Removed files from cache")

        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        try:
            src_dir_ = os.path.join(CACHE_DIR)
            prc_dir_ = os.path.join(PROCESSING_DIR)
            processing_files = os.listdir(prc_dir_)
            for pf in processing_files:
                shutil.move(
                    os.path.join(prc_dir_, pf), os.path.join(src_dir_, pf),
                )
        except BaseException:
            logging.error("Could not clean processing directory")
        raise
    finally:
        try:
            os.rmdir(PROCESSING_DIR)
        except OSError:
            pass
