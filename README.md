# sd<sup>2</sup>: Software Defined Software Development™
The Software Defined Software Development Process aka sd<sup>2</sup> is 
a modern Software Development approach that aims to simplify the 
complexity that usually accompanies working with multiple projects 
each with multiple branches and potentially each with its own
stack. sd<sup>2</sup> relies heavily on a **single** text 
file that describes a developer's development environments and in containers 
that isolate the different environments. sd<sup>2</sup> seperates the editing 
environment from the environment where compilation and testing takes place. 
In some sense, sd2 brings the advantages of a microservices environment to 
the development phase even when you do not use microservices in production.

## The Basic Concepts
In sd2 you split your editing, browsing and source control activities from all 
the other development activities. Editing is done on your developer 
workstation that we will call editing host or EH. All the other development 
activities will be done inside containers (DC) that can run anywhere you want. 
The containers run on hosts that we call development hosts (DH).

![Use Case](https://docs.google.com/drawings/d/1uO3umvqVMIM2HnrXJwRAgAX2UWRYNVqEKDTNggXlEIc/pub?w=960&h=720)

## sd2 advantages
1. First of all, sd2 builds on top of all the lightweight virtualization advantages:
    1. Start a development stack in mseconds, exactly the same stack you started last time.
    1. Keep multiple development stacks isolated from each other. 
    By separating EH and DH/DC you can now version independently your 
    EH from your DH & DC where your development environment runs. 
    So now you can work on multiple projects (or releases of the same project) 
    at the same time that have incompatible stacks.
    1. In a team environment, guarrantee that everybody has exactly the 
    same development stack independent of the editing environment they use.
1. sd2 uses a combination of tools to make sure that when you change a file on the EH, the file is copied to the destination(s) almost instanteneoulsy.
1. All generated files/artifacts are generated in the DHs. Since you only commit on EHs, there is no chance for accidentally commit generated artifacts.
1. Modern IDEs are heavyweight and have perofrmance requirements that increse with bigger projects. sd2 uses multiple replicas of the source code so both the IDE and the compilers/transpilers etc can work independently.

## Prerequisites
The tools have been tested on MacOS and Ubuntu hosts. At a minimum you 
need one machine (e.g. a MacOS notebook) with docker installed that will
 play the role of both the editing and the development machine.

1. Editing Host Requirements
   1. Python 2.7 with additional packages: python_hosts,jinja2,pyyaml
   1. fswatch (see [here](http://stackoverflow.com/questions/1515730/is-there-a-command-like-watch-or-inotifywait-on-the-mac))
   1. Add your user to sudoers (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
1. Development Host(s) Requirements
   1. Python 2.7 with additional packages: python_hosts,jinja2,pyyaml
   1. Add your user to sudoers (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
   1. ssh server
1. Other
   1. Before you start you need to make sure that you can use ssh with certificates to login from the editing machine to the development host(s). Do not add the hosts to .ssh/config or /etc/hosts.
   1. You also need to create your images. Here are some suggestions for images compatible with sd2
       1. The container will run as a daemon so put a `sleep infinity` at the end so it does not exit
       1. You will want to access inside the container so install ssh server and maybe vnc and/or screeen.
       1. Your container will run using the same username/id you have on the host. It is a good idea to use a script that relocates exising users in the container os that have the same userid with the one you have on the host (see [this tool](https://github.com/schmidigital/permission-fix/blob/master/tools/permission_fix).
       
## How to set it up
sd2 relies on a configuration file that defines your hosts, your conainers/images and your repositories. The configuration file should be in your home directory under .sd2 (ie ~/.sd2/config.yaml). A daemon called sd2d reads the configuration file and takes all the actions needed to maintain the connections and replicate the repositories in real time as they change in the development machine.

## What is not covered by sd<sup>2</sup>

1. Bring your own editor/IDE. We are agnostic how you edit your source code.
1. Bring your own container images. We do not provide tools to generate
 docker images, we expect that are already available and published in 
 a local or remote repository.
 
 ## FAQ
 1. When I run docker directly on the MacOS why can't I just mount the MacOS file system on the container?  
 This will work but in most cases, it will have sever performance implications. You ca read more about the issue [here](https://forums.docker.com/t/file-access-in-mounted-volumes-extremely-slow-cpu-bound/8076/174).
 1. Is sd2 secure when the development host is across the internet?  
 sd2 always uses ssh to communicate from the editing machine to the development machine so it is as secure as ssh itself.
 1. Why would I evet want to copy the files to the DH instead of the container itself?  
 The lifetime of a container is expected to be much shorter than the lifetime of a DH. 
 By replicating the repositories to the DH and mount them in the container you save the 
 time of continously replicating to new containers and save space when you want 
 multiple containers to access the same repository.
 
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
 1. The implemenation is in python but relies a lot on unix tools. I am sure people would want a Windows port.
