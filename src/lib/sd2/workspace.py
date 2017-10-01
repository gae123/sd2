#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

from . import myhosts

class Workspace(object):
    def __init__(self, node):
        self._node = node

    def get_targets(self):
        hosts = self._node.get('targets', [])

        for host in hosts:
            assert 'name' in host

        rr = [x for x in hosts if myhosts.is_enabled(x['name'])]
        rr = [x for x in rr if x.get('enabled', True) and not x.get('disabled', False)]
        #rr.extend([x for x in hosts if myhosts.exists_container(x['name']) ])
        return rr

    def is_enabled(self):
        if not self._node.get('enabled', True) or self._node.get('disabled', False):
            return False
        if not self.get_targets():
            return False     
        return True

