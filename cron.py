import datetime
import ipaddress
import logging
import socket
import uuid
from pathlib import Path

import pandas
import pytz
from sqlalchemy import func, false

from models import Session
from models.export_packet import Flow
from models.summary import SummaryMinute

logging.basicConfig(level=logging.INFO)

# constants
EPHEMERAL_PORT_RANGE_START = 32768
EPHEMERAL_PORT_RANGE_END = 65535

PROTOCOL_MAP = {
    # https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}

LOCAL_ADDRESS = [192, 168, 1]
DNS_CACHE = {}

LOCKFILE = Path("/tmp/ipfix-cron.lock")


# timestamp helper functions
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


# transformation helper functions
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
            split_source_address[: len(LOCAL_ADDRESS)] == LOCAL_ADDRESS
        ) or (split_source_address == [0, 0, 0, 0])
        destination_is_local = (
            split_destination_address[: len(LOCAL_ADDRESS)] == LOCAL_ADDRESS
        ) or (split_destination_address == [0, 0, 0, 0])
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
    else:
        # TODO: make this more accurate
        logging.warning(
            "IPv6 has no local address detection yet, "
            "keeping source as local and destination as remote: " + str(row)
        )
        return row["sourceAddress"], row["destinationAddress"], "unknown"


def get_domain_name(ip):
    try:
        return DNS_CACHE[ip]
    except KeyError:
        try:
            name, alias, addresslist = socket.gethostbyaddr(ip)
        except (socket.gaierror, socket.herror):
            name = ip
        DNS_CACHE[ip] = name
        return name


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


# loop function
def loop_minute(session, timestamp_from, timestamp_to):
    # read flows from db
    flows = pandas.read_sql(
        session.query(Flow)
        .filter(Flow.flowStartMilliseconds <= ts_to_ms(timestamp_to))
        .filter(Flow.flowEndMilliseconds >= ts_to_ms(timestamp_from))
        .statement,
        session.bind,
    )

    if len(flows) == 0:
        return

    # set the flow ids aside that are completely processed
    flow_ids = flows[flows["flowEndMilliseconds"] <= ts_to_ms(timestamp_to)]["id"]

    logging.info(
        "SummaryMinute: processing {} flows for {}".format(
            len(flows), timestamp_from.isoformat()
        )
    )

    # convert decimal IP addresses to strings
    ip_address_columns = [
        "sourceIPv4Address",
        "destinationIPv4Address",
        "sourceIPv6Address",
        "destinationIPv6Address",
    ]
    flows.loc[:, ip_address_columns] = flows.loc[:, ip_address_columns].applymap(
        convert_decimal_ip_address_to_string
    )

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
    flows.loc[:, mac_address_columns] = flows.loc[:, mac_address_columns].applymap(
        convert_decimal_mac_address_to_string
    )

    flows["destinationMacAddress"] = flows["destinationMacAddress"].fillna(
        flows["postDestinationMacAddress"]
    )

    # remove ephemeral ports for clarity
    port_columns = [
        "sourceTransportPort",
        "destinationTransportPort",
    ]
    flows.loc[:, port_columns] = flows.loc[:, port_columns].applymap(
        convert_ephemeral_ports
    )

    # set main port
    flows["port"] = flows[["sourceTransportPort", "destinationTransportPort"]].apply(
        set_main_port, axis="columns"
    )

    # set readable protocol
    flows["protocolIdentifier"] = flows["protocolIdentifier"].apply(convert_protocol)

    # set start and end timestamps within the time window
    flows["timestampStart"] = ts_to_ms(timestamp_from)
    flows["timestampStart"] = flows["timestampStart"].clip(
        lower=flows["flowStartMilliseconds"]
    )
    flows["timestampEnd"] = ts_to_ms(timestamp_to)
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

    # create summary
    groupby_columns = [
        "ipVersion",
        "protocolIdentifier",
        "localAddress",
        "localName",
        "remoteAddress",
        "remoteName",
        "port",
        "direction",
    ]
    sum_columns = ["octets", "packets", "connections"]
    summary = flows.groupby(by=groupby_columns).sum()[sum_columns].reset_index()

    # rounding
    summary["octets"] = summary["octets"].apply(lambda n: int(round(n, 0)))
    summary["packets"] = summary["packets"].apply(lambda n: int(round(n, 0)))

    # recreate column names
    index_columns = [
        "ip_version",
        "protocol",
        "local_address",
        "local_name",
        "remote_address",
        "remote_name",
        "port",
        "direction",
    ]
    summary.columns = index_columns + sum_columns
    summary = summary.set_index(index_columns)

    # set timestamp info
    summary["unix_start_ms"] = ts_to_ms(timestamp_from)
    summary["unix_end_ms"] = ts_to_ms(timestamp_to)
    summary["year"] = timestamp_from.astimezone(pytz.timezone("Europe/Brussels")).year
    summary["month"] = timestamp_from.astimezone(pytz.timezone("Europe/Brussels")).month
    summary["day"] = timestamp_from.astimezone(pytz.timezone("Europe/Brussels")).day
    summary["hour"] = timestamp_from.astimezone(pytz.timezone("Europe/Brussels")).hour
    summary["minute"] = timestamp_from.astimezone(
        pytz.timezone("Europe/Brussels")
    ).minute
    summary["offset"] = (
        timestamp_from.astimezone(pytz.timezone("Europe/Brussels"))
        .utcoffset()
        .total_seconds()
    )

    # generate new SummaryMinute.id
    summary["id"] = None
    summary["id"] = summary["id"].apply(lambda u: uuid.uuid4().hex)

    # remove obsolete SummaryMinutes
    session.query(SummaryMinute).filter(
        SummaryMinute.unix_start_ms == ts_to_ms(timestamp_from)
    ).filter(SummaryMinute.unix_end_ms == ts_to_ms(timestamp_to)).delete()
    session.commit()

    # add new SummaryMinutes
    summary.to_sql(SummaryMinute.__tablename__, session.bind, if_exists="append")

    # update Flow processed status
    session.bulk_update_mappings(
        Flow, [{"id": flow_id, "processed": True} for flow_id in flow_ids]
    )
    session.commit()


# main function
def create_summary_minute():
    session = Session()

    # set timestamps
    start_ts = (
        session.query(func.min(Flow.flowStartMilliseconds))
        .filter(Flow.processed == false())
        .first()[0]
    )
    start_ts = to_minute_start(ms_to_ts(start_ts))

    end_ts = (
        session.query(func.max(Flow.flowEndMilliseconds))
        .filter(Flow.processed == false())
        .first()[0]
    )
    end_ts = to_minute_end(ms_to_ts(end_ts))

    timestamp_from = start_ts
    timestamp_to = timestamp_from + datetime.timedelta(minutes=1)

    # start looping
    while timestamp_from < end_ts:
        loop_minute(session, timestamp_from, timestamp_to)
        timestamp_from = timestamp_from + datetime.timedelta(seconds=60)
        timestamp_to = timestamp_from + datetime.timedelta(seconds=60)


if __name__ == "__main__":
    if Path.exists(LOCKFILE):
        logging.error("Lockfile {} found, exiting...".format(LOCKFILE))
        exit(0)

    Path.touch(LOCKFILE)
    try:
        create_summary_minute()
    except BaseException:
        Path.unlink(LOCKFILE)
        raise
    else:
        Path.unlink(LOCKFILE)
