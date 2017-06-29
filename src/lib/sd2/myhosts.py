#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import sys
 
initialized = False
config_dct = {}
imagesdict = {}
containersdict = {}
hostsdict = {}
hosts = None

def init(a_config_dct=None):
    global config_dct, containersdict,hostsdict, imagesdict, initialized, hosts
    from . import config
    if a_config_dct is None:
        config_dct = config.read_config()
    else:
        config_dct = a_config_dct

    for image in config_dct.get('images', []):
        imagesdict[image['name']] = image

    hosts = config_dct.get('hosts', [])
    hostsdict = {x['name']: x for x in hosts}
    
    
    for ii,host in enumerate(hosts):
        base = host.get('base')
        host_name = host['name']
        config_containers = host.get('containers', [])
        if base is None and config_containers and not host.get('abstract'):
            msg = "Config Error: Non abstract Host {} has containers but not base\n"
            sys.stderr.write(msg.format(host_name))
            sys.exit(1)
        if base is not None:
            host['local-ip'] = "172.30.{}.100".format(base)
        containers = []
        for ii, imagename in enumerate(config_containers):
            image_name = imagename if isinstance(imagename,
                                                  basestring) else \
                        imagename['imagename']
            cont = {
                'ip': "172.30.{}.{}".format(base, 101 + ii),
                'image': imagesdict[image_name],
                'name': "{}-{}".format(host_name, (
                    ii if isinstance(imagename, basestring) else imagename.get(
                    'name', ii))),
                'upgrade': False if isinstance(imagename, basestring) else imagename.get('upgrade'),
                'host': host # The host where the container lives
            }
            containers.append(cont)
            containersdict[cont['name']] = cont
        host['containers'] = containers
    initialized = True

def exists_container(containerName):
    if not initialized:
        init()
    return containersdict.get(containerName)

def get_container_extra_flags(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('extra_flags', '')

def get_container_command(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('command', '')

def get_container_auth(containerName):
    if not initialized:
        init()
    cont = containersdict.get(containerName)
    return cont['image'].get('docker_auth')


def get_container_upgrade_flag(containerName):
    if not initialized:
        init()
    cont = containersdict.get(containerName)
    return cont.get('upgrade')

def get_container_docker_image(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image']['docker_name']

def get_container_ports(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('ports', [])

def get_container_env(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('env', [])

def get_container_ip(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['ip']

def get_container_names(hostname):
    if not initialized:
        init()
    host = hostsdict[hostname]
    return [x['name'] for x in host['containers']]

def is_disabled(hostname):
    assert isinstance(hostname, basestring)
    if not initialized:
        init()
    host = hostsdict.get(hostname)
    return not host or not not host.get('disabled')

def is_enabled(hostname):
    assert isinstance(hostname, basestring)
    if not initialized:
        init()
    host = hostsdict.get(hostname)
    if not host:
        cont = containersdict.get(hostname)
        if cont:
            host = cont['host']
    return host and not host.get('disabled')

def get_hosts(enabled=True):
    if not initialized:
        init()
    return [x for x in hosts if not enabled or is_enabled(x['name'])]

def get_hosts_dict(enabled=True):
    if not initialized:
        init()
    return {x['name']: x for x in get_hosts(enabled)}

def get_first_unused_base(dct):
    rr = []
    for host in dct.get('hosts', []):
        #print host['name']
        if host.get('base'):
            rr.append(host.get('base'))
    rr.sort()
    #print "Used bases: " + str(rr)
    for ii, num in enumerate(rr):
        assert num >= ii
        if num > ii:
            return ii
    return -1
        


    
