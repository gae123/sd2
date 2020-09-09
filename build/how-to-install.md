## Getting started

1. Download the `sd2.tar.gz` of your release and uncompress it/untar it (`tar -zxf`)
2. Copy the sd2 executable for your platform into a directory in your path (e.g. ~/bin)
   on your Editing Host (EH), no need to download the source code).
3. Create the configuration files in ~/.sd2 See the README in the first
   page for details.
4. Run the program in a terminal as 'sd2'. The program will run as a daemon.
    1. You can stop it with `sd2 halt`
    2. You can see logs with `sd2 logs`
    3. You can see the configuration used after the expansions with `sd2 --showconfig`
5. On MacOS there is a menu bar app called `sd2ui.app`. This provides a
   very basic UI to control and monitor sd2.

### Supported Platforms
* **Editing Host (EH)**: MacOS  & Linux (Linux is not tested regularly but should work)
* **Development Host (DH)**: Linux (MacOs should be easy but has not been tested) 

### Prerequisites
The tools have been tested on MacOS and Ubuntu hosts. In the simplest scenario you 
need one machine (e.g. a MacOS notebook) with docker installed that will
 play the role of both the editing and the development host.

1. Editing Host Requirements
   1. Make sure you have or install rsync
   1. Make sure you have or install the ssh client
   1. Install fswatch (see [here](http://stackoverflow.com/questions/1515730/is-there-a-command-like-watch-or-inotifywait-on-the-mac))
   1. Add your user to sudoers without a password requirement (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
1. Development Host(s) Requirements
   1. Install rsync, ssh server and docker
   1. Add your user to sudoers without a password requirement (see [here](https://askubuntu.com/questions/168461/how-do-i-sudo-without-having-to-enter-my-password))
1. Other
   1. Before you start you need to make sure that you can use ssh with  
      certificates to login from the editing machine to the development host(s). 
      Do not add the containers to .ssh/config or /etc/hosts, 
      the tool will take care of this.
   1. You also need to create your docker container image(s). 
      The image(s) will contain your 
      development environment. 
      Here are some suggestions to follow to make images compatible with 
      sd<sup>2</sup>:
       1. The container will run as a daemon so put a `sleep infinity` at the end 
       so it does not exit.
       1. You will want to access inside the container so install ssh server 
          and maybe vnc and/or screen.
       2. Install rsync if you plan to copy workspaces into the container.   
       3. Your container (DC) will run using the same username/id you have on the 
       host (DH). It is a good idea to use a script that relocates existing users 
       in the container os that have the same userid with the one you have 
       on the host (see [this](https://raw.githubusercontent.com/gae123/sd2/master/examples/entrypoint.sh).