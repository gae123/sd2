#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
from __future__ import absolute_import, print_function

import os
import sys
import six

import sd2
from .file_rewriter import FileRewriter

g_ssh_config_path = os.getenv('SD2_SSH_CONFIG',
    os.path.join(os.getenv('HOME'), '.ssh', 'config'))

container_entry_template = '''

host {cont[name]}
    HostName {cont[ip]}
    User {host[User]}
    Port {sshport}
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ConnectTimeout 5
'''
container_ssh_option_names = [
    'IdentityFile',
    "IdentitiesOnly",
    "PKCS11Provider",
    'ProxyCommand',
]

ssh_option_names = [
    'HostName',
    'Port',
    'User',
    'ServerAliveInterval',
    'StrictHostKeyChecking',
    'UserKnownHostsFile',
    'ConnectTimeout',
    'UseKeychain',
    'AddKeysToAgent',
    'ForwardAgent',
    'ProxyCommand',
    'ProxyJump',
    "PKCS11Provider",
    'SmartcardDevice',
    'HostKeyAlias',
    'LocalForward',
    'RemoteForward',
    'PubkeyAuthentication',
    'PreferredAuthentications'
]
ssh_option_names.extend(container_ssh_option_names)

def generate_host_entry(host, name, more, exclude):
    rr = ""
    rr += 'host {}\n'.format(name)
    for key, val in six.iteritems(host):
        if not key in ssh_option_names:
            continue
        if key.lower() in [x.lower() for x in exclude]:
            continue
        if not isinstance(val, (list, tuple)):
            val = [val]
        for vv in val:
            rr += '    {key} {value}\n'.format(key=key, value=vv)
    for entry in more:
        rr += entry + "\n"        
    rr += '\n'
    return rr

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
                    for key in six.viewkeys(match):
                        if not key in ssh_option_names:
                            continue
                        rr += '    {key} {value}\n'.format(key=key,
                                                           value=match[key])
                rr += '\n'
    
        rr += generate_host_entry(host, host['name'], [], ['LocalForward'])
        rr += 'host {}-ports\n'.format(host['name'])
        rr += "    LogLevel ERROR\n"
        if not 'HostName' in six.viewkeys(host):
            host['HostName'] = host['name']
        for key, val in six.iteritems(host):
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
        for key, val in six.iteritems(host):
            if key in container_ssh_option_names:
                rr += '    {} {}\n'.format(key, val)
    return rr


def get_our_ssh_config():
    rr = ''
    for host in sd2.get_hosts(enabled=False):
        if not host.get("User"):
            host['User'] = os.getenv('USER')
        try:
            rr += generate_for_host(host)
        except Exception as ex:
            sys.stderr.write("ERROR: Processing host {}\n".format(host['name']))
            raise
    
    return rr


def gen_ssh_config():
    if not os.path.exists(g_ssh_config_path):
        ssh_config_dir = os.path.dirname(g_ssh_config_path)
        if not os.path.exists(ssh_config_dir):
            os.system("mkdir -p {}".format(ssh_config_dir))
            os.system("chmod 700 {}".format(ssh_config_dir))
        os.system("touch {}".format(g_ssh_config_path))
    fr = FileRewriter(g_ssh_config_path)
    before, after = fr.read_config()
    rr = get_our_ssh_config()
    fr.write_config(
        before,
        rr.split('\n'),
        after
    )