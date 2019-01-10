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
    logging.warning("HH:SHOU %s", hostname)
    entry = unhealthy_hosts.get(hostname)
    if entry is None:
        entry = {
            'successes':0,
            'failures': 5 # very first time unhealthy? shut it down...
        }
        unhealthy_hosts[hostname] = entry 
    entry["failures"] += 1
    entry["timestamp"] = time.time()
    logging.warning("HH:SHOU:LL {} {}".format(hostname, entry))


def set_host_healthy(hostname):
    logging.debug("HH:SHOH %s", hostname)
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
    if (hostentry.get('failures') and 
        (time.time() - hostentry['timestamp']) < min(60 * 60, 2 ^ hostentry['failures'])) :
        logging.warning("HH:IHOU {} {}".format(hostname, hostentry))
        return False
    
    return True


def set_host_health(hostname, is_healthy):
    if is_healthy:
        set_host_healthy(hostname)
    else:
        set_host_unhealthy(hostname)    