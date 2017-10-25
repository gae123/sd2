#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
'''A mini database we use to make sure that the same hosts get the same IP
address all the time'''

import json
import os
import datetime
import time
import random
import logging

g_root_dir = os.getenv('SD2_CONFIG_DIR', os.path.join(os.getenv('HOME'), '.sd2'))

our_version = 1

def num_to_string_ip(address):
    return "{}.{}.{}.{}".format(
            (address & 0xFF000000) >> 24,
            (address & 0x00FF0000) >> 16,
            (address & 0x0000FF00) >> 8,
            address & 0x000000FF)

class Addressing(object):
    def __init__(self, path, mask=0xAC1E0000, bits=16):
        self.path = path
        self.mask = mask
        self.bits = bits

        if not os.path.exists(path):
            self.db = {
            'sd_db_version': our_version,
            'sd_db_mask': mask,
            'sd_db_bits': bits,
            'sd_db_hosts': {}
            }
            self.save()
        self.reload()

    def upgrade(self):
        self.db['sd_db_version'] = our_version

    def first_address(self):
        return self.mask + 2

    def last_address(self):
        return (self.mask | (2**self.bits - 1)) - 1

    def reload(self):
        with open(self.path, 'r') as fd:
            contents = fd.read()
            self.db = json.loads(contents)

        if self.db.get('sd_db_version') != our_version:
            self.upgrade()
            self.save()

    def has(self, hostname):
        return not not self.db['sd_db_hosts'].get(hostname) 

    def forget(self, hostname):
        if self.db['sd_db_hosts'].get(hostname):
            del self.db['sd_db_hosts'][hostname]
            self.save()

    def get_address(self):
        found = False
        while not found:
            found = True
            rint = random.randint(2, (2**self.bits)-2)
            assert rint
            address = mask | rint
            logging.debug("Considering 0x%x", address)

            for (name,host) in self.db['sd_db_hosts'].iteritems():
                if host['sd_db_address'] == address:
                    found = False
                    break
            if found:
                logging.debug("Returning 0x%x", address)
                return address

    def save(self):
        with open(path, 'w') as fd:
            fd.write(json.dumps(self.db, indent=4, sort_keys=True))

    def get_address_for_host(self, hostname):
        save = False
        host = self.db['sd_db_hosts'].get(hostname)
        if not host:
            save = True
            host = {
                'sd_db_name': hostname,
                'sd_db_address': self.get_address()
            }
        host['sd_db_string_address'] = num_to_string_ip(host['sd_db_address'])
        host['sd_db_last_used'] = int(time.time())
        self.db['sd_db_hosts'][hostname] = host
        if save:
            self.save()
        return host['sd_db_address']

    def get_text_address_for_host(self, hostname):
        address = self.get_address_for_host(hostname)
        return num_to_string_ip(address)


# Backwards compatibility
old_default_path = os.path.join(os.getenv('HOME'), '.config', '.sd2-cidr-db')
new_default_path = os.path.join(g_root_dir, '.sd2-cidr-db')
if (os.path.exists(old_default_path)) and not os.path.exists(new_default_path):
    os.system("mv {} {}", old_default_path, new_default_path)

path = os.getenv('SD2_CIDR_DB_PATH', new_default_path)
mask = os.getenv('SD2_CIDR_RPEFIX_MASK', 0xAC1E0000) # 172.30.x.x
bits = os.getenv('SD2_CIDR_RPEFIX_BITS', 16)
cidr_db = Addressing(path, mask, bits)