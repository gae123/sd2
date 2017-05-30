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

def init(a_config_dct = None):
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
        assert base is not None
        host['local-ip'] = "172.172.{}.100".format(base)
        containers = []
        host_name = host['name']
        for cont, imagename in enumerate(host.get('containers', [])):
            image_name = imagename if isinstance(imagename,
                                                  basestring) else \
                        imagename['imagename']
            cont = {
                'ip': "172.172.{}.{}".format(base, 101 + cont),
                'image': imagesdict[image_name],
                'name': "{}-{}".format(host_name, (
                    cont if isinstance(imagename, basestring) else imagename.get(
                    'name', cont))),
                'upgrade': False if isinstance(imagename, basestring) else imagename.get('upgrade')
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
    return host and not host.get('disabled')

def get_hosts(enabled=True):
    if not initialized:
        init()
    return [x for x in hosts if not enabled or is_enabled(x['name'])]

def get_hosts_dict(enabled=True):
    if not initialized:
        init()
    return {x['name']: x for x in get_hosts(enabled)}

    
