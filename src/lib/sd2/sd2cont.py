#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import os
import subprocess
import logging
import sys

def create_start_docker(args, hostname):
    from . import myhosts
    cmd = []
    ns_host_auth = myhosts.get_container_auth(hostname)
    if ns_host_auth:
        cmd.extend([
            ns_host_auth,
            ";"
        ])
    
    ns_host_ip = myhosts.get_container_ip(hostname)
    ports = myhosts.get_container_ports(hostname)
    ns_host_ports = ' '.join(['{}:{}'.format(ns_host_ip,x) for x in ports])
    ns_extra_args = myhosts.get_container_extra_flags(hostname)

    cmd.extend([
        'sudo',
        'docker',
        'run',
        '--detach',
        '--privileged',
        '--name={}'.format(hostname),
        '--hostname={}'.format(hostname),
        '--env', 'USER={}'.format(os.getenv('USER')),
        '--env', 'USER_ID={}'.format(
            subprocess.check_output(['id', '-u']).rstrip()),
        '--env', 'GROUP_ID={}'.format(
            subprocess.check_output(['id', '-g']).rstrip()),
        '--volume', '{}:/home/{}'.format(os.getenv('HOME'), os.getenv('USER'))
    ])
    if os.path.exists('/etc/localtime'):
        cmd.extend(['--volume', '/etc/localtime:/etc/localtime:ro'])
    if os.path.exists('/etc/timezone'):
        cmd.extend(['--volume', '/etc/timezone:/etc/timezone:ro'])
    if os.path.exists('/mnt'):
        cmd.extend(['--volume', '/mnt:/mnt'])

    for ports in ns_host_ports.split():
        cmd.append('--publish')
        cmd.append(ports)

    cmd.extend(['--workdir', '/home/' + os.getenv('USER')])
    cmd.append('--tty')
    if isinstance(ns_extra_args, basestring):
        ns_extra_args.split()
    for arg in ns_extra_args.split():
        cmd.append(arg)
    cmd.append(myhosts.get_container_docker_image(hostname))
    cmd.append(myhosts.get_container_command(hostname))

    command = ' '.join(cmd)
    if (not args.dryrun):
        logging.info("EXEC %s", command)
        os.system(command)
    else:
        print(command)

def find_id_of_container(container_name):
    containers = subprocess.check_output(
        ["sudo", "docker", "ps", "-qa"])
    cmd = [
        "sudo", "docker", "inspect", "-f",
        '{{.Id}},{{.Config.Hostname}}',
    ] + containers.split()
    inspout = subprocess.check_output(cmd)
    ids = [line.split(',')[0] for line in inspout.split() if
        line.split(',')[1].startswith(container_name)]
    return None if not ids else ids[0]

def remove_container_by_hostname(args, hostname):
    contid = find_id_of_container(hostname)
    cmd = "sudo docker rm -f " + contid
    if not args.dryrun:
        logging.debug("EXEC: {}".format(cmd))
        os.system(cmd)
    else:
        print(cmd)

def create_start_docker_if_needed(args, hostname):
    from . import myhosts
    running = None
    containers = subprocess.check_output(
        ["sudo", "docker", "ps", "-qa"])
    if containers:
        cmd = [
            "sudo", "docker", "inspect", "-f",
            '{{.State.Running}},{{.Config.Hostname}},{{.Config.Image}}',
        ] + containers.split()
        inspout = subprocess.check_output(cmd)
        running = [line.split(',')[0] for line in inspout.split() if
                            line.split(',')[1].startswith(hostname)]
        image = [line.split(',')[2] for line in inspout.split() if
                            line.split(',')[1].startswith(hostname)]

    create_new_one = False
    if running == ['true']:
        if image[0] == myhosts.get_container_docker_image(hostname):
            print(hostname + ': Found running...')
        else:
            print(hostname + ': Found running a different image {}.'.format(image))
            if args.upgrade or myhosts.get_container_upgrade_flag(hostname):
                print('{}: Removing container to start one with the right image {}'.format(
                    hostname, myhosts.get_container_docker_image(hostname)))
                remove_container_by_hostname(args, hostname)
                create_new_one = True
    else:
        if running == ['false']:
            print(hostname + ': Found stopped and removing. ')
            remove_container_by_hostname(args, hostname)
            create_new_one = True
        else:
            print(hostname + ': Not Found. ')
            create_new_one = True
    if create_new_one:
        print(hostname + ' Creating a new one...')
        create_start_docker(args, hostname)
    cmd = 'sudo docker exec -i -t {} su - {}'.format(
        hostname, os.getenv('USER'))
    print "Attach by running: '{}'".format(cmd)
    
    
def main(args):
    from . import gen_all, myhosts
    gen_all.gen_all()
    
    containers = []
    hostname = subprocess.check_output('hostname').rstrip()
    if not args.containers and args.all:
        containers = myhosts.get_container_names(hostname)
        if args.force:
            for cont in containers:
                cmd = "sudo docker rm -f " + cont
                if not args.dryrun:
                    logging.info("EXEC: " + cmd)
                    os.system(cmd)
                else:
                    print(cmd)
        for cont in containers:
            create_start_docker_if_needed(args, cont)
    if args.containers:
        for cont in args.containers:
            if not myhosts.exists_container(cont):
                cont2 = hostname + '-' + cont
            if not myhosts.exists_container(cont2):
                sys.stderr.write("Container {} is not known.\n".format(cont))
                sys.exit(1)
            else:
                cont = cont2
            create_start_docker_if_needed(args, cont)
    logging.debug("Starting %s", containers)
    
    
def add_argument_parsing(subparsers):
    parser_cont = subparsers.add_parser(
        'cont',
        description='Start containers in hosts'
    )
    parser_cont.add_argument('--force', '-f', action="store_true",
                             default=False,
                             help="first remove existing container if exists")
    parser_cont.add_argument('--upgrade', '-u', action="store_true",
                             default=False,
                             help="first remove existing container if exists and is different version")
    parser_cont.add_argument('--all', '-a', action="store_true", default=False,
                             help="Used to restart all containers in this host")
    parser_cont.add_argument("containers", nargs="*",
                             help="containers to start, leave it empty and pass --all to restart all of them",
                             default='')
    parser_cont.set_defaults(func=main)








