#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import logging
import subprocess
import fcntl
import os
import sys
import datetime
import copy
import json
import hashlib
import six

from .util import kill_subprocess_process
from . import myhosts
from . import util
from . import gen_ssh_config
from .connections import Connections
from .host_health import set_host_health, is_host_healthy

ON_POSIX = 'posix' in sys.builtin_module_names

def digest(obj):
    rr = []
    for option in (gen_ssh_config.ssh_option_names +
        ['disabled', 'enabled', 'name', 'base', 'sudo_ssh']):
        if obj.get(option):
            rr.append(obj.get(option))

    for entry in obj.get('containers', []):
        rr2 = []
        if entry.get('ip'):
            rr2.append(entry['ip'])
        if entry.get('image'):
            for option in ('ip', 'ports'):
                if entry['image'].get(option):
                    rr2.append(entry['image'][option])
        rr.append(sorted(rr2))
    return sorted(rr)

class SSHConnections(Connections):
    hosts_to_ssh = None
    def __init__(self, args):
        self.hosts_to_ssh = {}

    def init(self, args):
        previous_hosts_to_ssh = self.hosts_to_ssh
        self.hosts_to_ssh = {}
        for host in myhosts.hosts:
            if (util.is_localhost(host['name']) or
                myhosts.is_disabled(host['name']) or
                not myhosts.get_container_names(host['name'])):
                logging.debug('SSH:SKIP %s', host['name'])
                continue
            if not args.hosts or host['name'] in args.hosts:
                host['needsync'] = 1

                if host.get('sudo_ssh'):
                    sshcmd = "sudo ssh -F {}/.ssh/config".format(os.getenv('HOME'))
                else:
                    sshcmd = "ssh"

                self.hosts_to_ssh[host['name'] + '-ports'] = {
                    'name': host['name'] + '-ports',
                    'health_name': host['name'],
                    'sshcmd': sshcmd + ' -T ' + host['name'] + '-ports',
                    'ssh': {
                        'proc': None
                    },
                    '_digest': digest(host)
                }
                self.hosts_to_ssh[host['name'] + '-bridge'] = {
                    'name': host['name'],
                    'health_name': host['name'],
                    'sshcmd': 'ssh {} -T '.format(util.ssh_control_args(True)) + host['name'],
                    'ssh': {
                        'proc': None
                    },
                    '_digest': digest(host)
                }
        for name,host in six.iteritems(previous_hosts_to_ssh):
            if (self.hosts_to_ssh.get(name) and
                self.hosts_to_ssh.get(name)['_digest'] == host['_digest']):
                self.hosts_to_ssh.get(name)['ssh'] = host['ssh']
                logging.debug("Reusing host {}".format(name))
                continue
            logging.info("Shutting down ssh to host '{}'".format(name))
            proc = host['ssh']['proc']
            kill_subprocess_process(proc, "SSH {}".format(host['name']))

    def poll(self):
        for host in six.viewvalues(self.hosts_to_ssh):
            if host['ssh']['proc']:
                host['ssh']['proc'].poll()
                while (True):
                    try:
                        line = host['ssh']['proc'].stderr.readline()
                    except IOError:
                        break
                    if line:
                        logging.info("SSH {}: {}".format(host['name'], line))
                    else:
                        break
            # logging.info("%s %s",host, host['sshproc'].returncode if host['sshproc'] else '???')
            if host['ssh']['proc'] is None or host['ssh']['proc'].returncode != None:
                if host['ssh']['proc'] and host['ssh']['proc'].returncode != None:
                    log = logging.info if host['ssh']['proc'].returncode == 0 else logging.error
                    log("SSH:RC %s=%s",
                                 host['sshcmd'],
                                 host['ssh']['proc'].returncode)
                    set_host_health(host['health_name'],
                        not host['ssh']['proc'].returncode in (12, 255))

                    host['ssh']['proc'] = None
                # Only try to start once every 30 seconds
                if (host['ssh'].get('last_connection') and
                            (datetime.datetime.now() - host[
                                'ssh']['last_connection']).seconds < 30):
                    continue
                if not is_host_healthy(host['health_name']):
                    #logging.info("SSH:SKIP %s", host['sshcmd'])
                    continue
                else:
                    logging.info("SSH:START %s", host['sshcmd'])
                try:
                    host['ssh']['proc'] = subprocess.Popen(
                        host['sshcmd'],
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        close_fds=ON_POSIX)
                    host['ssh']['last_connection'] = datetime.datetime.now()
                except Exception as ex:
                    logging.warning("SSH:START:EXC: %s", ex)
                fl = fcntl.fcntl(host['ssh']['proc'].stderr, fcntl.F_GETFL)
                fcntl.fcntl(host['ssh']['proc'].stderr, fcntl.F_SETFL,
                            fl | os.O_NONBLOCK)

    def shutdown(self):
        for host in self.hosts_to_ssh.values():
            try:
                proc = host['ssh']['proc']
                kill_subprocess_process(proc, "SSH {}".format(host['name']))
            except:
                pass

