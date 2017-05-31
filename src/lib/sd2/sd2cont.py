#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import copy
import os
import logging
import sys

from . import util

def create_start_docker(host_name, container_host_name, dryrun=False):
    from . import myhosts, gen_interfaces
    if not dryrun:
        gen_interfaces.gen_interfaces(host_name)
    cmd = []
    ns_host_auth = myhosts.get_container_auth(container_host_name)
    if ns_host_auth:
        cmd.extend([
            ns_host_auth,
            ";"
        ])
    
    ns_host_ip = myhosts.get_container_ip(container_host_name)
    sshport = 22 if util.is_localhost(host_name) else 2222
    ports = copy.copy(myhosts.get_container_ports(container_host_name))
    ports.append("{}:22".format(sshport))
    ns_host_ports = ' '.join(['{}:{}'.format(ns_host_ip,x) for x in ports])
    ns_extra_args = myhosts.get_container_extra_flags(container_host_name)

    cmd.extend([
        'sudo',
        'docker',
        'run',
        '--detach',
        '--privileged',
        "--name={}".format(container_host_name),
        "--hostname={}".format(container_host_name),
        "--env", "USER=$USER",
        "--env", "USER_ID={}".format(
            util.remote_subprocess_check_output(host_name, ['id', '-u']).rstrip()),
        "--env", "GROUP_ID={}".format(
            util.remote_subprocess_check_output(host_name, ['id', '-g']).rstrip()),
        "--volume", "$HOME:/home/$USER"
    ])
    if util.remote_path_exists(host_name, '/etc/localtime'):
        cmd.extend(['--volume', '/etc/localtime:/etc/localtime:ro'])
    if util.remote_path_exists(host_name, '/etc/timezone'):
        cmd.extend(['--volume', '/etc/timezone:/etc/timezone:ro'])
    if util.remote_path_exists(host_name, '/mnt'):
        cmd.extend(['--volume', '/mnt:/mnt'])

    for ports in ns_host_ports.split():
        cmd.append('--publish')
        cmd.append(ports)

    cmd.extend(['--workdir', "/home/$USER"])
    cmd.append('--tty')
    if isinstance(ns_extra_args, basestring):
        ns_extra_args.split()
    for arg in ns_extra_args.split():
        cmd.append(arg)
    cmd.append(myhosts.get_container_docker_image(container_host_name))
    cmd.append(myhosts.get_container_command(container_host_name))

    command = ' '.join(cmd)
    if (not dryrun):
        logging.info("EXEC %s", command)
        util.remote_system(host_name, command)
        from .events import events
        events.emit({"hostname": container_host_name, "action": "start"})
    else:
        print(command)

def find_id_of_container(host_name, container_name):
    containers = util.remote_subprocess_check_output(host_name,
        ["sudo", "docker", "ps", "-qa"])
    cmd = [
        "sudo", "docker", "inspect", "-f",
        '{{.Id}},{{.Config.Hostname}}',
    ] + containers.split()
    inspout = util.remote_subprocess_check_output(host_name, cmd)
    ids = [line.split(',')[0] for line in inspout.split() if
        line.split(',')[1].startswith(container_name)]
    return None if not ids else ids[0]

def remove_container_by_hostname(host_name, container_host_name, dryrun):
    contid = find_id_of_container(host_name, container_host_name)
    cmd = "sudo docker rm -f " + contid
    if not dryrun:
        logging.debug("EXEC: {}".format(cmd))
        util.remote_system(host_name, cmd)
    else:
        print(cmd)

def create_start_docker_if_needed(host_name, container_host_name, dryrun, upgrade):
    rr = False
    from . import myhosts
    running = None
    containers = util.remote_subprocess_check_output(host_name,
        ["sudo", "docker", "ps", "-qa"])
    if containers:
        cmd = [
            "sudo", "docker", "inspect", "-f",
            '{{.State.Running}},{{.Config.Hostname}},{{.Config.Image}}',
        ] + containers.split()
        inspout = util.remote_subprocess_check_output(host_name, cmd)
        running = [line.split(',')[0] for line in inspout.split() if
                   line.split(',')[1].startswith(container_host_name)]
        image = [line.split(',')[2] for line in inspout.split() if
                 line.split(',')[1].startswith(container_host_name)]

    create_new_one = False
    if running == ['true']:
        if image[0] == myhosts.get_container_docker_image(container_host_name):
            print(container_host_name + ': Found running...')
        else:
            print(container_host_name + ': Found running a different image {}.'.format(image))
            if upgrade or myhosts.get_container_upgrade_flag(container_host_name):
                print('{}: Removing container to start one with the right image {}'.format(
                    container_host_name, myhosts.get_container_docker_image(container_host_name)))
                remove_container_by_hostname(host_name, container_host_name, dryrun)
                create_new_one = True
    else:
        if running == ['false']:
            print(container_host_name + ': Found stopped and removing. ')
            remove_container_by_hostname(host_name, container_host_name, dryrun)
            create_new_one = True
        else:
            print(container_host_name + ': Not Found. ')
            create_new_one = True
    if create_new_one:
        print(container_host_name + ' Creating a new one...')
        create_start_docker(host_name, container_host_name, dryrun)
        rr = True
    cmd = 'sudo docker exec -i -t {} su - {}'.format(
        container_host_name, os.getenv('USER'))
    print "Attach by running: '{}'".format(cmd)
    return rr
    

def do_containers(host, containers, force, dryrun, upgrade):
    if force:
        for cont in containers:
            cmd = "sudo docker rm -f " + cont
            if not dryrun:
                logging.info("EXEC: " + cmd)
                util.remote_system(host, cmd)
            else:
                print(cmd)
    ret = False
    for cont in containers:
        ret0 = create_start_docker_if_needed(host, cont, dryrun, upgrade)
        ret = ret or ret0
    return ret
    
    
def main(args):
    from . import gen_all, myhosts
    if not args.noinit:
        gen_all.gen_all()
    
    containers = []
    our_hostname = util.get_our_hostname()
    if not args.hostname:
        args.hostname = our_hostname
    if not args.containers and args.all:
        containers = myhosts.get_container_names(args.hostname)
    else:
        containers = args.containers
        
    # if the user just passed 0 convert it too hostname-0
    containers = [(x if x.startswith(args.hostname)
                    else (args.hostname + '-' + x)) for x in containers]
    ret = do_containers(args.hostname, containers, args.force, args.dryrun, args.upgrade)
    
    logging.debug("sd2cont: Starting %s on %s", containers, args.hostname)
    
    # 0 means it did start one or more
    sys.exit(0 if ret else 1)
    
    
def add_argument_parsing(subparsers):
    parser_cont = subparsers.add_parser(
        'cont',
        description='Start containers in hosts'
    )
    parser_cont.add_argument('--noinit', '-i', action="store_true",
                             default=False,
                             help="do not attempty to initialize /etc/hosts etc")
    parser_cont.add_argument('--force', '-f', action="store_true",
                             default=False,
                             help="first remove existing container if exists")
    parser_cont.add_argument(
        '--upgrade', '-u', action="store_true",
        default=False,
        help="first remove existing container if exists and is different version")
    parser_cont.add_argument('--all', '-a', action="store_true", default=False,
                             help="Used to restart all containers in this host")
    parser_cont.add_argument("hostname", nargs="?",
                             help="hostname where to start the images",
                             default='')
    parser_cont.add_argument(
        "containers", nargs="*",
        help="containers to start, leave it empty and pass --all to restart all of them",
        default='')
    parser_cont.set_defaults(func=main)








