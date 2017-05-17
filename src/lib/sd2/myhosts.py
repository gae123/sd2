#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################
import sys

from sd2 import config_dct

imagesdict = {}
for image in config_dct.get('images', []):
    imagesdict[image['name']] = image

hosts = config_dct.get('hosts', [])
hostsdict = {x['name']: x for x in hosts}

containersdict = {}
for host in hosts:
    try:
        base = host['base']
    except KeyError:
        sys.stderr.write("ERROR: base address for {} was not found.\n".format(host['name']))
        sys.exit(1)
    host['local-ip'] =  "172.172.{}.100".format(base)
    containers = []
    host_name = host['name']
    for cont,imagename in enumerate(host.get('containers', [])):
        cont = {
            'ip': "172.172.{}.{}".format(base, 101 + cont),
            'image': imagesdict[imagename] if isinstance(imagename,basestring) else imagesdict[imagename['imagename']],
            'image_name': imagename if isinstance(imagename,basestring) else imagename['imagename'],
            'name': "{}-{}".format(host_name, (cont if isinstance(imagename,basestring) else imagename['name'])),
        }
        containers.append(cont)
        containersdict[cont['name']] = cont
    host['containers'] = containers

def get_container_extra_flags(containerName):
    cont = containersdict[containerName]
    return cont['image'].get('extra_flags', '')

def get_container_command(containerName):
    cont = containersdict[containerName]
    return cont['image'].get('command', '')

def get_container_docker_image(containerName):
    cont = containersdict[containerName]
    return cont['image']['docker_name']

def get_container_ports(containerName):
    cont = containersdict[containerName]
    return cont['image'].get('ports', [])

def get_container_ip(containerName):
    cont = containersdict[containerName]
    return cont['ip']

def get_container_names(hostname):
    host = hostsdict[hostname]
    return [x['name'] for x in host['containers']]