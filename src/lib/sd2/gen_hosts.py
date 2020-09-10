#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017-2020 SiteWare Corp. All right reserved
#############################################################################
from __future__ import absolute_import, print_function

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
            for alias in cont.get('hostAliases', []):
                rr += "{}\t{}\n".format(host['local-ip'], alias)
        for cont in host['containers']:
            rr += '{}\t'.format(cont['ip'])
            rr += "{}\n".format(cont['name'])
            for alias in cont.get('aliases', []):
                rr += '{}\t'.format(cont['ip'])
                rr += "{} ".format(alias)
                rr += '\n'
    return rr

def gen_etc_hosts():
    fr = FileRewriter(g_etc_hosts)
    before, after = fr.read_config()
    rr = get_our_config()
    fr.write_config(
        before,
        rr.split('\n'),
        after,
        sudo=True
    )