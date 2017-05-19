#!/usr/bin/env python
# ifc.py

# sudo ip addr add 192.168.1.104/24 dev lo

import os
import sys
import sd2

if sys.argv[1] == 'Darwin':
    cmd = "sudo ifconfig lo0 alias {}"
else:
    cmd = "sudo ip addr replace {} dev lo"

for host in sd2.get_hosts():
    os.system(cmd.format(host['local-ip']))
    for cont in host.get('containers'):
        os.system(cmd.format(cont['ip']))

