#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import logging
import subprocess
import fcntl
import os
import sys

from .util import kill_subprocess_process
from . import myhosts
from . import util
from .connections import Connections

ON_POSIX = 'posix' in sys.builtin_module_names

g_args = None
g_workspaces = None

class SSHConnections(Connections):
    hosts_to_ssh = None
    def __init__(self, args, workspaces):
        global g_args, g_workspacesd
        g_args = args
        g_workspaces = workspaces
        self.hosts_to_ssh = {}
        for host in myhosts.hosts:
            if util.is_localhost(host['name']):
                continue
            if myhosts.is_disabled(host['name']):
                continue
            if not g_args.hosts or host['name'] in g_args.hosts:
                host['needsync'] = 1
                self.hosts_to_ssh[host['name']] = {
                    'name': host['name'],
                    'sshproc': None,
                    'sshcmd': 'sudo ssh -F ~/.ssh/config -T ' + host[
                        'name'] + '-ports'
                }

    def poll(self):
        for host in self.hosts_to_ssh.values():
            if host['sshproc']:
                host['sshproc'].poll()
                while (True):
                    try:
                        line = host['sshproc'].stderr.readline()
                    except IOError:
                        break
                    if line:
                        logging.info("SSH {}: {}".format(
                            host['name'], line))
                    else:
                        break
            # logging.info("%s %s",host, host['sshproc'].returncode if host['sshproc'] else '???')
            if host['sshproc'] is None or host['sshproc'].returncode != None:
                if host['sshproc'] and host['sshproc'].returncode != None:
                    log = logging.info if host['sshproc'].returncode == 0 else logging.error
                    log("SSH:RC %s=%s",
                                 host['sshcmd'],
                                 host['sshproc'].returncode)
                    host['sshproc'] = None
                # Only try to start once every 30 seconds
                if (host.get('ssh_last_connection') and
                            (datetime.datetime.now() - host[
                                'ssh_last_connection']).seconds < 30):
                    continue
                logging.info("SSH:START %s", host['sshcmd'])
                try:
                    host['sshproc'] = subprocess.Popen(
                        host['sshcmd'],
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        close_fds=ON_POSIX)

                except Exception as ex:
                    logging.warning("SSH:START:EXC: %s", ex)
                fl = fcntl.fcntl(host['sshproc'].stderr, fcntl.F_GETFL)
                fcntl.fcntl(host['sshproc'].stderr, fcntl.F_SETFL,
                            fl | os.O_NONBLOCK)

    def shutdown(self):
        for host in self.hosts_to_ssh.values():
            proc = host['sshproc']
            kill_subprocess_process(proc, "SSH {}".format(host['name']))