#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import sys
import platform
from . import util

from . import get_hosts

def gen_interfaces(hostname=None):
    if not hostname or util.is_localhost(hostname):
        hostplatform = platform.system()
    else:
        hostplatform = util.remote_subprocess_check_output(hostname, 'uname').rstrip()
    if hostplatform == 'Darwin':
        cmd = "sudo ifconfig lo0 alias {}"
    elif hostplatform == 'Linux':
        cmd = "sudo ip addr replace {} dev lo"
    else:
        sys.stderr.write('Unsupported platform ' + hostplatform)
        sys.exit(1)
    wholecmd = ''
    for host in get_hosts():
        if hostname and hostname != host['name']:
            continue
        wholecmd += cmd.format(host['local-ip']) + ';'
        for cont in host.get('containers'):
            wholecmd += cmd.format(cont['ip']) + ';'
    if wholecmd:
        util.remote_system(hostname, wholecmd)
        
    #import traceback
    #traceback.print_stack()