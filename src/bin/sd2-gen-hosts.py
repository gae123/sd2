#!/usr/bin/env python
# gen_hosts.py

import datetime

import sd2
from python_hosts import Hosts, HostsEntry

comment_magic = 'AUTOGEN-'

etchosts = Hosts()

# First remove the entries we already put there
names = [h.names[0] for h in etchosts.entries if (h and h.names and [x for x in h.names if comment_magic in x])]
for name in names:
    etchosts.remove_all_matching(name=name)

for host in sd2.get_hosts():
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
        #print "{}\t{}".format(cont['ip'], cont['name'])

etchosts.write()
