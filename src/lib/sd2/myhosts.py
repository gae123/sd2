#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import sys
import logging
import six
from . import addresses
 
initialized = False
config_dct = {}
imagesdict = {}
containersdict = {}
hostsdict = {}
hosts = None

def init(a_config_dct=None):
    global config_dct, containersdict,hostsdict, imagesdict, initialized, hosts
    from . import config
    initialized = False
    config_dct = {}
    imagesdict = {}
    containersdict = {}
    hostsdict = {}
    hosts = None
    if a_config_dct is None:
        config_dct = config.read_config()
    else:
        config_dct = a_config_dct

    for image in config_dct.get('images', []):
        imagesdict[image['name']] = image

    hosts = config_dct.get('hosts', [])
    hostsdict = {x['name']: x for x in hosts}
    
    for ii,host in enumerate(hosts):
        host_name = host['name']
        host['enabled'] = host.get('enabled', True) and not host.get('disabled', False)
        config_containers = host.get('containers', [])
        host['local-ip'] = addresses.cidr_db.get_text_address_for_host(host_name)
        containers = []
        for ii, container in enumerate(config_containers):
            image_name = container if isinstance(container, six.string_types) else \
                        container['imagename']
            aliases = [] if isinstance(container, six.string_types) else \
                        container.get('aliases', [])
            enabled = host['enabled']
            if isinstance(container, dict) and enabled:
                enabled = container.get('enabled', True) and not container.get('disabled', False)
            container_host_name = "{}-{}".format(host_name, (
                    ii if isinstance(container, six.string_types) else str(container.get(
                    'name', ii))))
            cont = {
                'ip': addresses.cidr_db.get_text_address_for_host(container_host_name),
                'image': imagesdict[image_name],
                'name': container_host_name,
                'remove_if_version_mismatch': False if isinstance(container, six.string_types) 
                                else container.get('remove_if_version_mismatch', False),
                'remove_if_running_when_disabled': (False if 
                                        isinstance(container, six.string_types) 
                          else container.get('remove_if_running_when_disabled', False)),
                'host': host, # The host where the container lives
                'enabled': enabled,
                'aliases': aliases
            }
            containers.append(cont)
            if containersdict.get(cont['name']):
                msg = "Container with name {}:{} is defined more that once.".format(
                                                    host_name, cont['name'])
                print(msg)
                logging.critical(msg)
                sys.exit(1) 
            containersdict[cont['name']] = cont
        host['containers'] = containers
    initialized = True

def exists_container(containerName):
    if not initialized:
        init()
    return containersdict.get(containerName)

def is_container_enabled(containerName):
    return containersdict.get(containerName).get('enabled', True)

def get_container_extra_flags(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    rr = cont['image'].get('extra_flags', '')
    if isinstance(rr, list):
        rr = " ".join(rr)
    return rr

def get_container_mount_home_dir(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('mount_home_dir', True)

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
    return cont.get('remove_if_version_mismatch')

def get_container_remove_flag(containerName):
    if not initialized:
        init()
    cont = containersdict.get(containerName)
    print(('*******'  + containerName + " " + str(cont)))
    return cont.get('remove_if_running_when_disabled', False)

def get_container_docker_image(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('docker_name') or cont['image'].get('docker_image_name')

def get_container_ports(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['image'].get('ports', [])

def get_container_env(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    environ = cont['image'].get('environ')
    if environ is None:
        return cont['image'].get('env', [])
    rr = [{"name": x.split(":")[0], "value": x[x.find(":") + 1:]} for x in environ]
    return rr

def get_container_ip(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['ip']

def get_container_aliases(containerName):
    if not initialized:
        init()
    cont = containersdict[containerName]
    return cont['aliases']

def get_container_names(hostname):
    if not initialized:
        init()
    host = hostsdict[hostname]
    return [x['name'] for x in host['containers']]

def is_disabled(hostname):
    return not is_enabled(hostname)

def is_enabled(hostname):
    assert isinstance(hostname, six.string_types)
    if not initialized:
        init()
    host = hostsdict.get(hostname)
    if not host:
        host = containersdict.get(hostname)
    if not host:
        return False
    if host['name'] != hostname:
        logging.critical("{} {}".format(host['name'], hostname))
        assert False
    return host and host.get('enabled', True)

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
        


    
