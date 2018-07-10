#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
"""A small cache that keeps track of unhealthy hosts and backs off from using
them"""

import time
import logging

unhealthy_hosts = {}


def set_host_unhealthy(hostname):
    logging.warning("SHOU %s", hostname)
    entry = unhealthy_hosts.get(hostname)
    if entry is None:
        entry = {
            'successes':0,
            'failures': 5 # very first time unhealthy? shut it down...
        }
        unhealthy_hosts[hostname] = entry 
    entry["failures"] += 1
    entry["timestamp"] = time.time()


def set_host_healthy(hostname):
    logging.warning("SHOH %s", hostname)
    entry = unhealthy_hosts.get(hostname)
    if entry is None:
        entry = {
            'timestamp': time.time(),
            'successes': 0,
        }
        unhealthy_hosts[hostname] = entry
    entry['successes'] += 1
    entry['failures'] = 0


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

def set_host_health(hostname, is_healthy):
    if is_healthy:
        set_host_healthy(hostname)
    else:
        set_host_unhealthy(hostname)    