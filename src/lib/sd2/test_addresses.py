#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import logging

import pytest
from . import addresses

def test_pytest():
    assert True

def test_object_exists():
    assert addresses.cidr_db

def test_new_address():
    address = addresses.cidr_db.get_address_for_host('test_test_foo')
    assert address
    assert address >= addresses.cidr_db.first_address()
    assert address <= addresses.cidr_db.last_address()

    addresses.cidr_db.reload()
    assert addresses.cidr_db.get_address_for_host('test_test_foo') == address

    assert addresses.cidr_db.has('test_test_foo')
    addresses.cidr_db.forget('test_test_foo')
    assert not addresses.cidr_db.has('test_test_foo')

    addresses.cidr_db.reload()
    assert not addresses.cidr_db.has('test_test_foo')    
