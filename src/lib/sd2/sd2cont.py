#!/usr/bin/env python
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

import copy
import os
import logging
import sys
import subprocess
import six

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
    ns_aliases = myhosts.get_container_aliases(container_host_name)

    cmd.extend([
        'sudo',
        'docker',
        'run',
        '--detach',
        '--privileged',
        "--name={}".format(container_host_name),
        "--hostname={}".format(container_host_name),
    ])
    for alias in ns_aliases:
        cmd.append("--add-host='{alias}:{ip}'".format(alias=alias, ip=ns_host_ip))

    if myhosts.get_container_mount_home_dir(container_host_name):
        cmd.extend(["--volume", "$HOME:/home/$USER"])
    if util.remote_path_exists(host_name, '/mnt'):
        cmd.extend(['--volume', '/mnt:/mnt'])

    for ports in ns_host_ports.split():
        cmd.append('--publish')
        cmd.append(ports)
        
    env = {
        "SD2IP": ns_host_ip
    }
    env.update()
    for var in myhosts.get_container_env(container_host_name):
        env[var['name']] = var['value']
    for kk,vv in six.iteritems(env):
        cmd.append("--env")
        cmd.append("{}={}".format(kk,vv))

    cmd.extend(['--workdir', "/home/$USER"])
    cmd.append('--tty')
    if isinstance(ns_extra_args, six.string_types):
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

def create_start_docker_if_needed(host_name, container_host_name, dryrun):
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
                   line.split(',')[1] == container_host_name]
        image = [line.split(',')[2] for line in inspout.split() if
                 line.split(',')[1] == container_host_name]

    create_new_one = False
    if running == ['true']:
        remove = False
        if (image[0] == myhosts.get_container_docker_image(container_host_name) and
            myhosts.is_container_enabled(container_host_name)):
            print((container_host_name + ': Found running...'))
        else:
            if (not myhosts.is_container_enabled(container_host_name)):
                print((container_host_name + ': Found running when it should not.'))
                reason = " because it should not be running"
                remove = myhosts.get_container_remove_flag(container_host_name)
            else:
                print((container_host_name + ': Found running a different image {}.'.format(image)))
                reason = 'to start one with the right image {}'.format(
                        myhosts.get_container_docker_image(container_host_name))
                remove = myhosts.get_container_upgrade_flag(container_host_name)
        if remove:
            print(('{}: Removing container {}'.format(container_host_name, reason)))
            remove_container_by_hostname(host_name, container_host_name, dryrun)
            create_new_one = myhosts.is_container_enabled(container_host_name)
    elif running == ['false']:
        create_new_one = myhosts.is_container_enabled(container_host_name)
        print((container_host_name + 
            ': Found stopped and removing. ({})'.format(create_new_one)))
        remove_container_by_hostname(host_name, container_host_name, dryrun)
    else:
        create_new_one = myhosts.is_container_enabled(container_host_name)
        print((container_host_name + 
            ': Not Found. ({})'.format('NOT OK' if create_new_one else 'OK')))
    if create_new_one:
        print((container_host_name + ' Creating a new one...'))
        create_start_docker(host_name, container_host_name, dryrun)
        rr = True
        cmd = 'sudo docker exec -i -t {} su - {}'.format(
            container_host_name, os.getenv('USER'))
        print(("Attach by running: '{}'".format(cmd)))
    return rr
    

def do_containers(host, containers, force, dryrun):
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
        ret0 = create_start_docker_if_needed(host, cont, dryrun)
        ret = ret or ret0
    return ret

def check_for_prereqs():
    tools_found = True
    for tool in [
        ['ssh', 'Please install ssh and restart..'],
        ['rsync', 'Please install rsync and restart..'],
        ['fswatch', 'Please install fswatch and restart..'],
    ]:
        try:
            rr = subprocess.check_output("type {}".format(tool[0]), shell=True)
        except Exception as ex:
            sys.stdout.write("{}\n".format(tool[1]))
            tools_found = False
    if not tools_found:
        sys.exit(1)
    
    
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
    ret = do_containers(args.hostname, containers, args.force, args.dryrun)
    
    logging.debug("sd2cont: Considered %s on %s", containers, args.hostname)
    
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
    
    parser_cont.add_argument('--all', '-a', action="store_true", default=False,
                             help="Used to restart all containers in this host")
    parser_cont.add_argument("hostname", nargs="?",
                             help="hostname where to start the images",
                             default='')
    parser_cont.add_argument(
        "containers", nargs="*",
        help="containers to start, leave it empty and pass --all to restart all of them",
        default='')
    parser_cont.set_defaults(func=main, logging=True)








