#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
from __future__ import absolute_import, print_function

import logging

class Events(object):
    """A very simple events mechanism"""
    def __init__(self):
        self._listeners = []
        
    def listen(self):
        listener = []
        self._listeners.append(listener)
        return listener
    
    def stop_listening(self, listener):
        for ii,alistener in enumerate(self._listeners):
            if alistener is listener:
                self._listeners.pop(ii)
                return listener
        return None
    
    def emit(self, event):
        logging.debug("EV:EMIT %s %s", event, len(self._listeners))
        for listener in self._listeners:
            listener.append(event)
            
    def is_event_pending(self, listener):
        return not not len(listener)
    
    def get_pending_event(self, listener):
        event = listener.pop(0)
        logging.debug("EV:READ %s %s", event, len(listener))
        return event
    
events = Events()