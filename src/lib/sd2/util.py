#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import os
import logging
import subprocess

from .host_health import set_host_health, is_host_healthy

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
        os.system("sudo pkill -P {}".format(proc.pid))
        logging.debug("KILL %s %s", label, proc.pid)
    except:
        logging.warning("KILL:FAIL %s", label)
        pass
    
# Closure to cache local host name and avoid local
def _our_host_name():
    class O(object):
        our_host_name = None
        
    o = O()
    def our_host_name_inner(o):
        def fn():
            if o.our_host_name is None:
                o.our_host_name = subprocess.check_output('hostname') \
                                            .decode('ascii') \
                                            .rstrip() \
                                            .split('.')[0]
            return o.our_host_name
        return fn
    return our_host_name_inner(o)
get_our_hostname = _our_host_name()

def is_localhost(hostname):
    if hostname == "localhost":
        return True
    if hostname == get_our_hostname():
        return True
    return False


def remote_system(remote_host, cmd):
    if isinstance(cmd, (list, tuple)):
        cmd = " ".join(cmd)
    if remote_host and not is_localhost(remote_host):
        cmd = "ssh {} {} '{}'".format(ssh_control_args(), remote_host, cmd)
        if not is_host_healthy(remote_host):
            logging.debug("RSYS SKIP: " + cmd)
            return
    logging.debug("RSYS: " + cmd)
    rr = os.system(cmd)
    logging.debug("RSYS: {} rr={}".format(cmd, rr))
    set_host_health(remote_host,
        not(rr == 255 and not is_localhost(remote_host)))
    return rr


def remote_subprocess_check_output(remote_host, cmd):
    if isinstance(cmd, (list, tuple)):
        cmd = " ".join(cmd)
    if remote_host and not is_localhost(remote_host):
        cmd = "ssh {} {} '{}'".format(ssh_control_args(), remote_host, cmd)
    if not is_host_healthy(remote_host):
        logging.debug("RSCO SKIP: " + cmd)
        return ''
    else:
        logging.debug("RSCO: " + cmd)
    try:
        output = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as ex:
        set_host_health(remote_host, ex.returncode != 255)
        logging.error("RSCO FAILED cmd=%s rc=%d '%s'", cmd, ex.returncode, ex.output)
        return ''
    return output


def remote_path_exists(remote_host, path):
    if is_localhost(remote_host):
        return os.path.exists(path)
    else:
        cmd = "ssh {} {} '[ -e {} ] && echo yes'".format(ssh_control_args(), remote_host, path)
        output = subprocess.check_output(cmd, shell=True)
        return output.rstrip() == 'yes'


def system(what, cmd):
    try:
        logging.info('{} {}'.format(what, cmd))
        output = subprocess.check_output(cmd, shell=True)
        logging.info(output)
    except subprocess.CalledProcessError as ex:
        logging.error("FAILED: rc=%d '%s'", ex.returncode, ex.output)


def ssh_control_args(master=False):
    return '-o ControlMaster={} -o  ControlPath=~/.ssh/control:%h:%p:%r'.format(
        'yes' if master else 'no'
    )

