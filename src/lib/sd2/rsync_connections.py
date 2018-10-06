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

from .util import kill_subprocess_process, ssh_control_args
from .workspace import Workspace
from .connections import Connections
from .host_health import set_host_health, is_host_healthy
from . import myhosts

ON_POSIX = 'posix' in sys.builtin_module_names


def slash_ending(path):
    if not path.endswith(os.path.sep):
        path += os.path.sep
    return path

# For rsync --exclude and --include are followed in order. If something is
def get_rsync_cmd(ws, host, args):
    cmd = ['rsync',
           '-rlptgozv'
           ]
    if args.dryrun:
        cmd.append('--dry-run')
    for paths in ws.get('paths'):
        if paths.get('include'):
            for path in paths.get('include'):
                cmd.append('--include=' + path)
        elif paths.get('exclude'):
            for path in paths.get('exclude'):
                cmd.append('--exclude=' + path)
    if ws.get('delete'):
        cmd.append('--delete')
        cmd.append('--force-delete')
    if not args.nossh:
        cmd.append('-e')
        cmd.append('ssh {}'.format(ssh_control_args()))
    path = os.path.join(ws['source_root'], ws.get("source", ""))
    cmd.append(slash_ending(path))
    dest_root = ws.get('dest_root', ws['source_root']).replace(os.environ.get('HOME'), '~')
    cmd.append("{}:{}".format(host['name'],
            slash_ending(os.path.join(dest_root, ws.get("source", "")))))
    return cmd


class RsyncConnections(Connections):
    singleton = None
    def __init__(self, args, workspaces, periodInSeconds):
        logging.info("RSYNC:CONSTR:EE {}".format(periodInSeconds))
        from .events import events
        self.periodInSeconds = periodInSeconds
        self._args = args
        self._workspaces = []
        for wsi in workspaces:
            if not Workspace(wsi).is_enabled():
                logging.info('RSYNC:SKIP {} '.format(wsi['name']))
                continue
            for host in Workspace(wsi).get_targets():
                if not wsi in self._workspaces:
                    self._workspaces.append(wsi)
        self._listener = events.listen()
        # for x in self._workspaces:
        #     print {'name': x['name'], 'source_root': x['source_root'], 'targets': x['targets']}
        # sys.exit(0)

    def handle_host(self, wsi, host):
        if self._args.hosts and not host['name'] in self._args.hosts:
            return
        if not myhosts.is_enabled(host['name']):
            #logging.debug("RSYNC:SKIP {}".format(host['name']))
            return

        proc = host.get('rsyncproc')
        if proc:
            proc.poll()
            while (True):
                try:
                    line = proc.stdout.readline()
                except IOError:
                    break
                if line:
                    logging.info("RSYNC {} - {}: {}".format(
                        wsi['name'], host['name'], line.rstrip()))
                else:
                    break
            if proc.returncode is None:
                # logging.debug("SKIP:SYNC %s:%s", wsi['name'], host['name'])
                return
            else:
                log = logging.info if proc.returncode == 0 else logging.error
                log("RSYNC:RC %s:%s=%s", wsi['name'],
                             host['name'],
                             proc.returncode)
                host['rsyncproc'] = None
                host['lastsync'] = datetime.datetime.now()
                host['lastrc'] = proc.returncode
                set_host_health(host['name'], proc.returncode == 0)

        # Every 15 minutes rsync
        period = self.periodInSeconds if host.get('lastrc',1) == 0 else 30
        if (host.get('lastsync') and
                    (datetime.datetime.now() - host[
                        'lastsync']).seconds > period):
            host['needsync'] = 1
        if host.get('needsync') == 0:
            return
        if not is_host_healthy(host['name']):
            logging.warning("RSYNC: SKIP {}".format(host['name']))
            host['needsync'] = 0
            host['lastsync'] = datetime.datetime.now()
            return
        cmd = get_rsync_cmd(wsi, host, self._args)
        logging.info("RSYNC {}:{} {}".format(wsi['name'],
                                             host['name'], " ".join(cmd)))
        host['rsyncproc'] = subprocess.Popen(cmd,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT,
                                             close_fds=ON_POSIX)
        fl = fcntl.fcntl(host['rsyncproc'].stdout, fcntl.F_GETFL)
        fcntl.fcntl(host['rsyncproc'].stdout, fcntl.F_SETFL,
                    fl | os.O_NONBLOCK)
        host['needsync'] = 0

    def poll(self):
        from .events import events
        while events.is_event_pending(self._listener):
            event = events.get_pending_event(self._listener)
            logging.debug("RSYNC EV %s", event)
            if event["action"] != "start":
                continue
            for wsi in self._workspaces:
                for host in Workspace(wsi).get_targets():
                    if host['name'].startswith(event['hostname']):
                        host['needsync'] = 1

        for wsi in self._workspaces:
            for host in Workspace(wsi).get_targets():
                self.handle_host(wsi, host)

    def shutdown(self):
        for wsi in self._workspaces:
            for host in Workspace(wsi).get_targets():
                proc = host.get('rsyncproc')
                kill_subprocess_process(
                    proc,
                    "RSYNC {} {}".format(host['name'], wsi['name']))

    def wake(self, workspace=None):
        for wsi in self._workspaces:
            if workspace and wsi != workspace:
                continue
            for host in Workspace(wsi).get_targets():
                host['needsync'] = 1


