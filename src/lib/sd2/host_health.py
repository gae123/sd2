#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
"""A small cache that keeps track of unhealthy hosts and backs off from using
them"""

import time

unhealthy_hosts = {}


def set_host_unhealthy(hostname):
    entry = unhealthy_hosts.get(hostname)
    if entry is None:
        entry = {
            'timestamp': 0,
            'failures': 0
        }
        unhealthy_hosts[hostname] = entry 
    entry["failures"] += 1
    entry["timestamp"] = time.time()


def is_host_healthy(hostname):
    hostentry = unhealthy_hosts.get(hostname)
    if hostentry is None:
        return True
    if time.time() - hostentry['timestamp'] > 60 * 60:
        del unhealthy_hosts[hostname]
        return True
    if hostentry['failures'] < 3:
        return True
    return False