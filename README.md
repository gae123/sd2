[![Build Status](https://travis-ci.org/gae123/sd2.svg?branch=master)](https://travis-ci.org/gae123/sd2)

# sd<sup>2</sup>: Software Defined Software Development™
The Software Defined Software Development Process aka sd<sup>2</sup> and pronounced 
sd-square is 
a modern Software Development approach. It aims to assist developers 
who work concurrently with multiple source bases, 
each with multiple branches and potentially its own technology
stack. 

sd<sup>2</sup> relies heavily on a **single** text configuration
file that describes a developer's development environments. It also relies
 heavily on containers 
that isolate the different environments. sd<sup>2</sup> seperates the editing 
environment from the environment where compilation and testing takes place. 
In some sense, sd2 brings the advantages of a microservices environment to 
the development phase even when you do not use microservices in your
architecture.

This repository provides a tool called `sd2` that assists developers embracing the
sd<sup>2</sup> process.

## The Basic Concepts
In sd<sup>2</sup> you split your editing, browsing and source control activities from all 
the other development activities. Editing is done on your developer 
workstation that we will call editing host(EH). All the other development 
activities are performed containers (DC) that can run anywhere you want. 
The containers run on hosts that we call development hosts (DH).

![Use Case](https://docs.google.com/drawings/d/1uO3umvqVMIM2HnrXJwRAgAX2UWRYNVqEKDTNggXlEIc/pub?w=960&h=720)

## sd2 advantages
1. First of all, sd2 builds on top of all the lightweight virtualization advantages:
    1. Start a development stack in milliseconds, exactly the same stack you started last time.
    1. Keep multiple development stacks isolated from each other. 
    By separating EH and DH/DC you can now version independently your 
    EH from your DH & DC where your development environment runs. 
    So now you can work on multiple projects (or releases of the same project) 
    with incompatible stacks at the same time.
    1. In a team environment, sd<sup>2</sup> guarrantee that every
     developer has exactly the 
    same development stack independent of the editing environment they use.
1. sd2 uses a combination of tools to make sure that when you change a file on 
the EH, the file is copied to the destination(s) almost instanteneoulsy.
1. All generated files/artifacts are generated in the DHs. Since you only 
commit on EHs, there is no chance for accidentally commit generated artifacts.
1. Modern IDEs are heavyweight and have perofrmance requirements that increase 
with bigger projects. sd2 uses multiple replicas of the source code so both the 
IDE and the compilers/transpilers etc can work independently.

## Supported Platforms
* **Editing Host (EH)**: MacOS  (Linux should be easy but has not been tested)
* **Development Host (DH)**: Linux (MacOs should be easy but has not been tested) 

## Prerequisites
The tools have been tested on MacOS and Ubuntu hosts. In the simplest scenario you 
need one machine (e.g. a MacOS notebook) with docker installed that will
 play the role of both the editing and the development host.

1. Editing Host Requirements
   1. Install rsync & ssh client
   1. Install fswatch (see [here](http://stackoverflow.com/questions/1515730/is-there-a-command-like-watch-or-inotifywait-on-the-mac))
   1. Add your user to sudoers without a password requirement (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
1. Development Host(s) Requirements
   1. Install rsync, ssh server and docker
   1. Add your user to sudoers (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
1. Other
   1. Before you start you need to make sure that you can use ssh with  
      certificates to login from the editing machine to the development host(s). 
      Do not add the hosts to .ssh/config or /etc/hosts, the tool will take care of this.
   1. You also need to create your container image(s). The image(s) will contain your 
      development environment. Evertyhing but your IDE should be there.
      Here are some suggestions to follow to make images compatible with 
      sd<sup>2</sup>:
       1. The container will run as a daemon so put a `sleep infinity` at the end 
       so it does not exit.
       1. You will want to access inside the container so install ssh server 
          and maybe vnc and screeen.
       1. Install rsync if you plan to copy workspaces into the container.   
       1. Your container will run using the same username/id you have on the 
       host. It is a good idea to use a script that relocates exising users 
       in the container os that have the same userid with the one you have 
       on the host (see [this](https://raw.githubusercontent.com/gae123/sd2/master/examples/entrypoint.sh).
       
## How to set it up
sd2 relies on a configuration file that defines your DHs, your conainers/images 
and your repositories/workspaces. The configuration file needs to be in your home directory 
under .sd2 (ie ~/.sd2/config.yaml). 

A daemon called sd2 reads the configuration 
file and takes all the actions needed to maintain the connections and replicate 
the repositories in real time as they change in the development machine.
If you change the configuration file, the daemon automatically will change what 
it is doing to match the new configuration.

You can download the appropriate sd2 binary for your platform 
from the [releases](https://github.com/gae123/sd2/releases) section. Put it
somewhere so that it is in your PATH, create your configuration file that 
describes your environment, open a terminal and run sd2 from the command line.

## Configuration 

**Location**: When sd2 starts it reads its configuration from `~/.sd2/config.yaml` 
(or in `$SD2_CONFIG_DIR/config.yaml` if this variable is set). 


**Syntax**: This file
has three main sections. One that describes the DHs, one that describes the 
containers images, and one that describes the workspaces that you want to be
synced into the DHs. There is a json schema for the file that you can find
[here](https://raw.githubusercontent.com/gae123/sd2/master/src/lib/sd2/config_schema.json).

**Examples**
A very simple configuration file is shown 
[here](https://raw.githubusercontent.com/gae123/sd2/master/examples/config-1/config.yaml)
It will start two containers on a host called paros that run an image 
that has ubuntu 16.04, ssh and nginx.
The first container will be called paros-0 and the second will be called paros-1. From the
EH, you
should be able to ssh to paros-0 and paros-1. You will find yourself in your
own home directory in paros, using your username. On your EH 
you should be able to open 
a browser and point it to http://paros-0 or http://paros-1 and see the nginx
page.

A second example is shown 
[here](https://raw.githubusercontent.com/gae123/sd2/master/examples/config-2/config.yaml). 
It builds on the first one by adding two workspaces *0.sd2* and *1.sd2* that are
replicated into the containers under /tmp. Note how the workspaces 
configuration sections are built using inheritance
to avoid replicating the "exclude" paths.  *0.sd2* and *1.sd2* inherit from *sd2* which
inherits from *any*.

Another example shown
[here](https://raw.githubusercontent.com/gae123/sd2/master/examples/config-2/config.yaml)
shows two images *ubuntu1404* and *ubuntu1604*. It also adds four containers
*paros-0*, *paros-1*, *paros-2* and *paros-3*. *paros-0* and *paros-1* use the 
*ubuntu1404*
image. The other two containers use the *ubuntu1604* image.
Finally, there are two workspaces *0.sd2* and *1.sd2*. *0.sd2* is replicated to *paros-0*
and *paros-2*. *1.sd2* is replicated to *paros-1* and *paros-3*.


## Advanced Configuration Topics
**Expansion**:
String values are treated as [python string templates](https://docs.python.org/2/library/string.html#template-strings) with the already parsed
config file as the context. So for instance if you put `$name` or `${name}` somewhere it will
be substituted by the earlier value of name. (If you need to 
use the dollar sign character `$$` to escape `$`). Environment variables are also
available this way.

**Jinja Template Support**
If the config.yaml file starts with the line `#!jinja2`
sd2 treats the configuration file as a [jinja2 template](http://jinja.pocoo.org/docs/2.9/). 
The tool first processes the jinja2 file
and then parses it as yaml. 
 
 By default, a dictionary with the environment variables
is passed as the context for the jinja2 template rendering. So for instance if
you have `{{USER}}` in the file it will be substituted with the USER environment
variable.

Furthermore, if there is an executable called ~/.sd2/config,
the executable is first executed, and its output is treated as json. Then this json
is parsed and provided as context to the the jinja2 parser. This allows to do 
very cool initializations.

**Inheritance**
In the workspaces and hosts section you can create abstract sections that do 
not describe a workspace or host but provide some key/values pairs that will 
be inherited later.

**Multiple configuration files**
If the tool finds more that one files in ~/.sd2 that end with `config.yaml`
it will read and parse all the files and merge them together. This is a great
way to separate the configuration of unrelated projects.

## What is not covered by sd<sup>2</sup>
1. Bring your own editor/IDE. sd<sup>2</sup> is agnostic on how you edit your source code.
1. Bring your own container images. sd<sup>2</sup> does not provide tools to generate
 docker images, we expect that are already available and published in 
 a local or remote repository.
1. Although this might change in the future, you are currently responsible to
   set up your DH (a DH really only needs an account with your user name,
   ssh access and docker + rsync installed).
 
 
## Troubleshooting
1. Start the commaind as following `sd2 -l debug` to see what it is doing
1. Start the command as `sd2 --showconfig`. It will show the config file
as it is after substitutions and will exit.
1. Start the command as `sd2 --showschema`. It will show the json schema file.
1. Try to ssh to the DHs. You should be able to ssh to any of them from a 
terminal in your EH.
1. You can access a container in a DH with the following command:  
`ssh -t <<DH>> sudo docker exec -it <<CONTAINER NAME>>  su - $USER`  
Of course in the local case you do not need the ssh part. This is the preferred
way to get shell access to the container.
1. You can see the containers running on a DH by runnign `sudo ssh <<DH>> sudo docker ps`
1. You can delete all the containers runnin on a DH by running 
`sudo ssh <<DH>> 'sudo docker rm -f $(docker ps -qa)'`
 
## FAQ
1. When I run docker directly on the MacOS why can't I just mount the MacOS 
file system on the container?  
This will work but in most cases, it will have severe performance implications. 
You can read more about the issue [here](https://forums.docker.com/t/file-access-in-mounted-volumes-extremely-slow-cpu-bound/8076/174).
1. Is sd2 secure when the development host is across the internet?  
sd2 always uses ssh to communicate from the editing machine to the 
development machine so it is as secure as ssh itself.
1. Why would I ever want to copy the files to the DH instead of the container itself?  
The lifetime of a container is expected to be much shorter than the lifetime of a DH. 
By replicating the repositories to the DH and mount them in the container you save the 
time of continously replicating to new containers and save space when you want 
multiple containers to access the same repository.
1. What are the system files that sd2 alters:
    1. `/etc/hosts`
    1. `~/.ssh/config`  
    
    All the changes are done in a very safe way that does not alter what is 
    already in the files.
1. What IP addresses do the containers use?  
    The system automatically assigns addresses in the 172.30.X.X private address
    range. It uses the 3rd octet for the DH and the 4 octet for the containers.
 
## Future Directions
1. Many times I have thought that this separation should take one more step
where the development environment can be different from the execution environment.
In this directions, you have EH, DH, DC and one more set of environments called ECs 
where the code runs. Currently the generated artifacts are deployed in 
the DC itself that plays a dual role.
1. Many frameworks, e.g. kubernetes and swarm slightly overlap on the container
lifetime management. For now, I have decided to keep things simple and only rely
on ssh & friends but I can see how in the future this could be expanded to embrace
and leverage such frameworks.
1. The implemenation is in python but relies a lot on unix tools. I am 
sure people would want a Windows port.

## For developers
1. Build the source code by running `cd build; make`
1. The main program is in bin/sd2 start from there
1. When ready to push change the version number at the top of build/Makefile and run `make push`
