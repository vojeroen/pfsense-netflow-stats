import logging
import socket

from cachetools import cached, TTLCache


@cached(cache=TTLCache(maxsize=1024 * 1024, ttl=900))
def get_domain_name(ip):
    logging.debug("Retrieving domain name for " + ip)
    try:
        name, alias, addresslist = socket.gethostbyaddr(ip)
    except (socket.gaierror, socket.herror):
        name = ip
    return name
