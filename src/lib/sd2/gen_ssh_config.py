#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import datetime
import os
import sys

import sd2

g_seperator_start = '################# SDSD starts here - DO NOT CHANGE BELOW #######################'
g_seperator_end = '################# SDSD ends here - DO NOT CHANGE ABOVE ########################'
g_ssh_config_path = os.path.join(os.getenv('HOME'), '.ssh', 'config')


# Read .ssh config
def read_ssh_config():
    with open(g_ssh_config_path, 'r') as fd:
        rr = fd.readlines()
    rr = [x.rstrip() for x in rr]
    before = []
    after = []
    mode = 'before'
    for line in rr:
        if mode == 'before':
            if line != g_seperator_start:
                before.append(line)
            else:
                mode = 'during'
        elif mode == 'during':
            if line == g_seperator_end:
                mode = 'after'
        else:
            assert mode == 'after'
            after.append(line)
    
    return (before, after)


def write_ssh_config(before, rr, after):
    with open(g_ssh_config_path, 'w') as fd:
        for line in (before +
                         [g_seperator_start,
                          "# Generated on {}".format(datetime.datetime.now())
                          ] +
                         rr +
                         [g_seperator_end] +
                         after):
            fd.write(line + '\n')


def read_and_split_ssh_config():
    contents = read_ssh_config()


container_entry_template = '''

host {cont[name]}
    HostName {cont[name]}
    User {host[User]}
    Port 2222
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    IdentityFile {host[IdentityFile]}
    ServerAliveInterval 60
'''

ssh_option_names = [
    'HostName',
    'Port',
    'User',
    'IdentityFile',
    'ServerAliveInterval',
    'StrictHostKeyChecking',
    'UserKnownHostsFile'
]


def get_our_ssh_config():
    rr = ''
    for host in sd2.get_hosts():
        from . import util
        if util.is_localhost(host['name']):
            continue
        try:
            rr += '''\n########## GENERATED DO NOT MODIFY #####################\n'''
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
            
            rr += 'host {}-ports\n'.format(host['name'])
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
                for port in ports:
                    (p1, p2) = port.split(':')
                    rr += (
                    "    LocalForward  {0}:{1} {0}:{1}\n".format(cont['name'],
                                                                 p1))
            rr += '\n'
            
            for cont in host.get('containers', []):
                rr += container_entry_template.format(**locals())
        except Exception as ex:
            sys.stderr.write("ERROR: Processing host {}\n".format(host['name']))
            raise
    
    return rr


def gen_ssh_config():
    before, after = read_ssh_config()
    rr = get_our_ssh_config()
    write_ssh_config(
        before,
        rr.split('\n'),
        after
    )