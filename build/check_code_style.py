#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import sys

filepath = sys.argv[1]
with open(filepath) as ff:
    lines = ff.read()
    
lines = lines.split('\n')
for ii,line in enumerate(lines):
    for jj,ch in enumerate(line):
        if ch == '\t':
            sys.stderr.write(
                "{}:{}:{} is a leading tab\n".format(sys.argv[1], ii+1, jj))
            sys.exit(1)
        if ch.isspace():
            continue
        break
    # Sigh there is no way to make a string multiline in json
    if filepath.endswith('.json'):
        continue
    if len(line) > 100:
        sys.stderr.write(
            "{}:{} is too long\n".format(sys.argv[1], ii+1))
        sys.exit(1)