#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import os
import sys

import sd2
from .file_rewriter import FileRewriter

g_ssh_config_path = os.path.join(os.getenv('HOME'), '.ssh', 'config')

container_entry_template = '''

host {cont[name]}
    HostName {cont[name]}
    User {host[User]}
    Port {sshport}
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ConnectTimeout 5
'''

ssh_option_names = [
    'HostName',
    'Port',
    'User',
    'IdentityFile',
    'ServerAliveInterval',
    'StrictHostKeyChecking',
    'UserKnownHostsFile',
    'ProxyCommand',
    'ConnectTimeout',
    'UseKeychain',
    'AddKeysToAgent',
    'ForwardAgent',
    "PKCS11Provider"
]

def generate_for_host(host):
    from . import util
    rr = ''
    rr += '''\n########## GENERATED DO NOT MODIFY #####################\n'''
    sshport = 22 if util.is_localhost(host['name']) else 2222
    if not util.is_localhost(host['name']):
        if host.get('match'):
            matches = host.get('match')
            for hostname in [host['name'], host['name'] + '-ports']:
                for match in matches:
                    rr += 'Match originalhost {hostname} exec "{match[condition]}"\n'.format(
                        hostname=hostname, match=match)
                    for key in match.keys():
                        if not key in ssh_option_names:
                            continue
                        rr += '    {key} {value}\n'.format(key=key,
                                                           value=match[key])
                rr += '\n'
    
        rr += 'host {}\n'.format(host['name'])
        for key, val in host.iteritems():
            if not key in ssh_option_names:
                continue
            if not isinstance(val, (list, tuple)):
                val = [val]
            for vv in val:
                rr += '    {key} {value}\n'.format(key=key, value=vv)
        rr += '\n'
    
        if host.get('containers'):
            rr += 'host {}-ports\n'.format(host['name'])
            if not 'HostName' in host.keys():
                host['HostName'] = host['name']
            for key, val in host.iteritems():
                if not key in ssh_option_names + ['LocalForward']:
                    continue
                if not isinstance(val, (list, tuple)):
                    val = [val]
                for vv in val:
                    rr += '    {key} {value}\n'.format(key=key, value=vv)
                    # rr += '    LocalForward {}-local:2375 localhost:2375\n'.format(host['name'])
            for cont in host.get('containers', []):
                ports = cont['image'].get('ports', [])
                for port in ports + ["{}:22".format(sshport)]:
                    (p1, p2) = port.split(':')
                    rr += (
                        "    LocalForward  {0}:{1} {2}:{1}\n".format(
                            cont['name'], p1, cont['ip']))
            rr += '\n'

    for cont in host.get('containers', []):
        rr += container_entry_template.format(**locals())
        for key, val in host.iteritems():
            if key in ['IdentityFile','ProxyCommad','PKCS11Provider']:
                rr += '    {} {}\n'.format(key, val)
    return rr


def get_our_ssh_config():
    rr = ''
    for host in sd2.get_hosts():
        if not host.get("User"):
            host['User'] = os.getenv('USER')
        try:
            rr += generate_for_host(host)
        except Exception as ex:
            sys.stderr.write("ERROR: Processing host {}\n".format(host['name']))
            raise
    
    return rr


def gen_ssh_config():
    fr = FileRewriter(g_ssh_config_path)
    before, after = fr.read_config()
    rr = get_our_ssh_config()
    fr.write_config(
        before,
        rr.split('\n'),
        after
    )