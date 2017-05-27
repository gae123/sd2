#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

class Connections(object):
    
    def poll(self):
        raise NotImplementedError()
    
    def shutdown(self):
        raise NotImplementedError()