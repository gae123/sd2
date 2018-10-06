#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import logging
import sys
import datetime
import fcntl
import subprocess
import os
import six

from .util import kill_subprocess_process
from .connections import Connections
from .host_health import set_host_unhealthy, is_host_healthy, set_host_healthy
from . import myhosts

ON_POSIX = 'posix' in sys.builtin_module_names

g_args = None
g_workspaces = None


class DockerConnections(Connections):
    singleton = None
    host_to_contact = None
    def __init__(self, args, workspaces, periodInSeconds):
        global g_args, g_workspaces
        logging.info("DOCK:CONSTR:EE {}".format(periodInSeconds))
        g_args = args
        g_workspaces = workspaces
        self.periodInSeconds = periodInSeconds
        self.host_to_contact = {}
        for host in myhosts.get_hosts():
            if not myhosts.get_container_names(host['name']):
                logging.debug('DOCK:SKIP %s', host['name'])
                continue
            if not g_args.hosts or host['name'] in g_args.hosts:
                self.host_to_contact[host['name']] = {
                    'name': host['name'],
                    'proc': None,
                    'need_connection': 1,
                    'cmd': self.get_cmd(host)
                }

    def get_cmd(self, host):
        rr = [sys.argv[0]]
        rr.extend([
            "--level",
            g_args.level
        ])
        rr.extend([
                "cont",
                '--noinit',
                '--all',
                host['name']
                ])
        return rr

    def handle_host(self, host):
        proc = host.get('proc')
        if proc:
            proc.poll()
            while (True):
                try:
                    line = proc.stdout.readline()
                except IOError:
                    break
                if line:
                    log = logging.error if 'error' in line.lower() else logging.info
                    log("DOCKER {}: {}".format(host['name'], line.rstrip()))
                else:
                    break
            if proc.returncode is None:
                # logging.debug("SKIP:SYNC %s:%s", wsi['name'], host['name'])
                return
            else:
                log = logging.info if proc.returncode in (0,1) else logging.error
                log("DOCKER:RC %s=%s",
                             host['name'],
                             proc.returncode)
                host['proc'] = None
                host['last_connection'] = datetime.datetime.now()
                if proc.returncode == 12:
                    set_host_unhealthy(host['name'])
                elif proc.returncode == 0:
                    set_host_healthy(host['name'])
                    # from .events import events
                    # events.emit(
                    #     {"hostname": host['name'], "action": "start"})

        # Every so many seconds repeat
        if (host.get('last_connection') and
                    (datetime.datetime.now() - host[
                        'last_connection']).seconds > self.periodInSeconds):
            host['need_connection'] = 1
        if host.get('need_connection') == 0:
            return
        if not is_host_healthy(host['name']):
            logging.warning("DOCKER:SKIP {}".format(host['name']))
            host['need_connection'] = 0
            host['last_connection'] = datetime.datetime.now()
            return
        cmd = host['cmd']
        logging.info("DOCKER:START {} {}".format(host['name'], " ".join(cmd)))
        host['proc'] = subprocess.Popen(cmd,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         close_fds=ON_POSIX)
        fl = fcntl.fcntl(host['proc'].stdout, fcntl.F_GETFL)
        fcntl.fcntl(host['proc'].stdout, fcntl.F_SETFL,
                    fl | os.O_NONBLOCK)
        host['need_connection'] = 0

    def poll(self):
        for host in six.viewvalues(self.host_to_contact):
            self.handle_host(host)

    def shutdown(self):
        for host in six.viewvalues(self.host_to_contact):
            proc = host.get('proc')
            kill_subprocess_process(
                proc,
                "DOCKER {} ".format(host['name']))

    def wake(self):
        for host in six.viewvalues(self.host_to_contact):
            host['need_connection'] = 1