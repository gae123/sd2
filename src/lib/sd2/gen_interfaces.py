#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import os
import sys
import platform

from . import get_hosts

def gen_interfaces():
    if platform.system() == 'Darwin':
        cmd = "sudo ifconfig lo0 alias {}"
    elif platform.system() == 'Linux':
        cmd = "sudo ip addr replace {} dev lo"
    else:
        sys.stderr.write('Unsupported platform ' + platform.system())
        sys.exit(1)
    for host in get_hosts():
        os.system(cmd.format(host['local-ip']))
        for cont in host.get('containers'):
            os.system(cmd.format(cont['ip']))