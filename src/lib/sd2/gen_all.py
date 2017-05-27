#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

def gen_all(args=None):
    from .gen_hosts import gen_etc_hosts
    from .gen_ssh_config import gen_ssh_config
    from .gen_interfaces import gen_interfaces
    
    gen_interfaces()
    gen_etc_hosts()
    gen_ssh_config()
    

def add_argument_parsing(subparsers):
    parser_init = subparsers.add_parser(
        'init',
        description='Read the config file and initialize ')
    parser_init.set_defaults(func=gen_all)