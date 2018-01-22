#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import os
from . import get_hosts
from .file_rewriter import FileRewriter

g_etc_hosts = os.getenv('SD2_ETC_HOSTS', '/etc/hosts')    
    
def get_our_config():
    rr = ''
    for host in get_hosts(enabled=False):
        if not host.get('containers'):
            continue
        rr += '{}\t{}\n'.format(host['local-ip'], host['name'] + '-local')
        for cont in host['containers']:
            rr += '{}\t{}\n'.format(cont['ip'], cont['name'])
    return rr

def gen_etc_hosts():
    fr = FileRewriter('/etc/hosts')
    before, after = fr.read_config()
    rr = get_our_config()
    fr.write_config(
        before,
        rr.split('\n'),
        after,
        sudo=True
    )