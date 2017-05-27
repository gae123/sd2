#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import os
from . import get_hosts

def gen_etc_hosts():
    from python_hosts import Hosts, HostsEntry
    
    comment_magic = 'AUTOGEN-'
    
    etchosts = Hosts()
    
    # First remove the entries we already put there
    names = [h.names[0] for h in etchosts.entries if
             (h and h.names and [x for x in h.names if comment_magic in x])]
    for name in names:
        etchosts.remove_all_matching(name=name)
    
    for host in get_hosts():
        etchosts.add(
            [HostsEntry(
                entry_type='ipv4',
                address=host['local-ip'],
                names=[host['name'] + '-local', comment_magic + host['name']],
                # comment="{} {}".format(
                #     comment_magic,
                #     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # )
            )]
        )
        for cont in host['containers']:
            etchosts.add(
                [HostsEntry(
                    entry_type='ipv4',
                    address=cont['ip'],
                    names=[cont['name'], comment_magic + cont['name']],
                    # comment="{} {}".format(
                    #     comment_magic,
                    #     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # )
                )]
            )
            # print "{}\t{}".format(cont['ip'], cont['name'])
    
    etchosts.write('/tmp/sd2hosts')
    os.system('sudo mv /tmp/sd2hosts /etc/hosts')