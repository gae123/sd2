#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
'''In this module we start/stop hosts when they are disabled/enabled'''
import logging
import os

from . import myhosts
from . import util
from .connections import Connections

class HostConnections(Connections):
    def __init__(self, args, workspaces):
        for host in myhosts.get_hosts(enabled=False):
            logging.debug("HC:CONS %s", host)
            if util.is_localhost(host['name']):
                logging.debug("HC:SKIP %s", host['name'])
                continue
            if myhosts.is_disabled(host['name']):
                cmd = host.get('operations', {}).get('stop')
                if not cmd:
                    continue
                util.system('HC:STOP {}'.format(host['name']), cmd)
            else:
                cmd = host.get('operations', {}).get('start')
                if not cmd:
                    continue
                util.system('HC:START {}'.format(host['name']), cmd)

    def poll(self):
        pass

    def shutdown(self):
        pass
