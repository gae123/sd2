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

from .util import kill_subprocess_process
from .workspace import Workspace
from .connections import Connections
from . import myhosts

ON_POSIX = 'posix' in sys.builtin_module_names

g_args = None
g_workspaces = None

def slash_ending(path):
    if not path.endswith(os.path.sep):
        path += os.path.sep
    return path

# For rsync --exclude and --include are followed in order. If something is
def get_rsync_cmd(ws, host):
    cmd = ['rsync',
           '-rlptgoOzv'
           ]
    if g_args.dryrun:
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
    if not g_args.nossh:
        cmd.append('-e')
        cmd.append('ssh')
    path = os.path.join(ws['source_root'], ws.get("source", ""))
    cmd.append(slash_ending(path))
    dest_root = ws.get('dest_root', ws['source_root']).replace(os.environ.get('HOME'), '~')
    cmd.append("{}:{}".format(host['name'],
            slash_ending(os.path.join(dest_root, ws.get("source", "")))))
    return cmd


class RsyncConnections(Connections):
    def __init__(self, args, workspaces):
        from .events import events
        global g_args, g_workspaces
        g_args = args
        g_workspaces = workspaces
        self._listener = events.listen()

    def handle_host(self, wsi, host):
        if g_args.hosts and not host['name'] in g_args.hosts:
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

        # Every 15 minutes rsync
        period = 15*60 if host.get('lastrc',1) == 0 else 30
        if (host.get('lastsync') and
                    (datetime.datetime.now() - host[
                        'lastsync']).seconds > period):
            host['needsync'] = 1
        if host.get('needsync') == 0:
            return
        cmd = get_rsync_cmd(wsi, host)
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
            if event["action"] != "start":
                continue
            for wsi in g_workspaces:
                for host in Workspace(wsi).get_targets():
                    if host['name'].startswith(event['hostname']):
                        host['needsync'] = 1
        
        for wsi in g_workspaces:
            for host in Workspace(wsi).get_targets():
                self.handle_host(wsi, host)

    def shutdown(self):
        for wsi in g_workspaces:
            for host in Workspace(wsi).get_targets():
                proc = host.get('rsyncproc')
                kill_subprocess_process(
                    proc,
                    "RSYNC {} {}".format(host['name'], wsi['name']))