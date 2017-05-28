#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import os
import logging
import subprocess

# def resync_reg_exp_match(root, apath, ipath):
#     if not apath.startswith(root):
#         return False
#     rpath = apath[len(root)-1:]
#     aipath = ipath.split('/')
#     arpath = rpath.split('/')
#     while len(aipath) and len(arpath):
#         if aipath[0] == arpath[0]:
#             aipath.pop(0)
#             arpath.pop(0)
#             continue
#         if ipath[0] == '*':
#             aipath.pop(0)
#             arpath.pop(0)
#             continue
#         if aipath[0] == '**':
#             while len(aipath) and len(arpath) and

def convert_rsync_to_regex(path):
    rr = path
    if not rr.startswith('/'):
        rr = '**/' + rr
    rr = rr.replace('.', '\\.')
    rr = rr.replace('**', '__EVERYTHING__')
    rr = rr.replace('*', '__ONELEVEL__')
    rr = rr.replace('__EVERYTHING__', '.*')
    rr = rr.replace('__ONELEVEL__', '[^/]*')
    return rr


def _glob_to_regex(ss):
    rr = ss.replace('.', '\\.')
    rr = rr.replace('*', '.*')
    return rr

def kill_subprocess_process(proc, label=''):
    try:
        if not proc:
            return
        proc.poll()
        if proc.returncode is not None:
            return
        #proc.kill()
        os.system("sudo kill {}".format(proc.pid))
    except:
        logging.warning("KIILL:FAIL %s", label)
        pass
    
# Closure to cache local host name and avoid local
def _our_host_name():
    class O(object):
        our_host_name = None
        
    o = O()
    def our_host_name_inner(o):
        def fn():
            if o.our_host_name is None:
                o.our_host_name = subprocess.check_output('hostname').rstrip().split('.')[0]
            return o.our_host_name
        return fn
    return our_host_name_inner(o)
get_our_hostname = _our_host_name()


def remote_system(remote_host, cmd):
    if get_our_hostname() != remote_host:
        if isinstance(cmd, (list,tuple)):
            cmd = " ".join(cmd)
        cmd = "ssh {} {}".format(remote_host, cmd)
    return os.system(cmd)


def remote_subprocess_check_output(remote_host, cmd):
    if get_our_hostname() != remote_host:
        if isinstance(cmd, (list,tuple)):
            cmd = " ".join(cmd)
        cmd = "ssh {} {}".format(remote_host, cmd)
    output = subprocess.check_output(cmd, shell=True)
    return output