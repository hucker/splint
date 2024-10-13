"""
This module provides functions for using ping to verify network connectivity.


"""

import ping3

from .splint_result import SR
from .splint_format import SM

NO_HOSTS_MSG = "No hosts provided for ping."
MIN_LATENCY_MS = 0.0001


def rule_ping_check(hosts: str | list, timeout_ms: float = 4000.0, skip_on_none=False, fail_on_none=False) -> SR:
    """
    Given a sequence of hosts perform ping checks against each of them given a single timeout
    value.  This function handles the following:
    hosts = "google.com"   converted to ["google.com"]
    hosts = "google.com apple.com"   converted to ["google.com","apple.com"]
    hosts = ["google.com"]   as is
    Args:
        hosts: string with list of hosts or list of hosts
        timeout_ms: Time in milliseconds.
    Yields:
        list of results
    """
    hosts = hosts.split() if isinstance(hosts, str) else hosts

    if len(hosts) == 0:
        if skip_on_none:
            yield SR(status=True, skipped=True, msg=NO_HOSTS_MSG)
            return
        else:
            yield SR(status=not fail_on_none, msg=NO_HOSTS_MSG)
            return

    for host in hosts:
        try:
            latency = ping3.ping(host, timeout=timeout_ms, unit='ms')

            if latency is False:
                yield SR(status=False, msg=f"No ping response from server {SM.code(host)} timeout = {timeout_ms:0.1f} ms")
            elif latency < MIN_LATENCY_MS:
                latency_str = f"{MIN_LATENCY_MS:0.1f}"
                yield SR(status=True, msg=f"Host {SM.code(host)} is up: response time < {SM.code(latency_str)} ms")
            else:
                latency_str = f"{latency:0.1f}"
                yield SR(status=True, msg=f"Host {SM.code(host)} is up, response time = {SM.code(latency_str)} ms")
        except Exception:
            # Document your exception handling logic here
            yield SR(status=False, msg=f"Host {SM.code(host)} not found: {SM.fail(host)}")
