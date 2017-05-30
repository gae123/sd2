#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import datetime
import os

g_seperator_start = '#### SDSD starts here - DO NOT CHANGE BELOW #######################'
g_seperator_end = '#### SDSD ends here - DO NOT CHANGE ABOVE ########################'

class FileRewriter(object):
    def __init__(self, path):
        self.path = path

    def read_config(self):
        with open(self.path, 'r') as fd:
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

    def write_config(self,before, rr, after, sudo=False):
        import tempfile
        path = tempfile.mkstemp()[1]
        with open(path, 'w') as fd:
            for line in (before +
                             [g_seperator_start,
                              "# Generated on {}".format(
                                  datetime.datetime.now())
                              ] +
                             rr +
                             [g_seperator_end] +
                             after):
                fd.write(line + '\n')
        os.system("{} mv {} {}.bk".format(
            'sudo' if sudo else '',
            self.path, self.path))
        os.system("{} mv {} {}".format(
            'sudo' if sudo else '',
            path, self.path))
    