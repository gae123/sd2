## The entrypoint.sh file

The entrypoint.sh file is an entrypoint script for docker images that you
need to use interactively and is used in many of the examples. It is also very
useful in conjuction with sd2.

The file is very valuable even independently of sd2. It can do the following:
1. Make sure that the started docker image has a USER like the one in the host
1. Run a shell script
1. Start the docker image with an ssh daemon running
1. Start the docker image and provide a command line

All these are controlled by environment variables you pass when you start
your container. Here is an example:

```
wget -O ~/.tmp_entrypoint.sh \
   https://raw.githubusercontent.com/gae123/sd2/master/examples/entrypoint.sh
chmod +x ~/.tmp_entrypoint.sh
docker run --name=mycontainer \
           --hostname=mycontainer \
           --volume $HOME:/home/$USER  \
           --env GROUP_ID=$(id -g) \
           --env USER_ID=$(id -u) \
           --env USER=$USER \
           --env SD2_EP_SHELL=1 \
           --env SD2_EP_TZ=America/Los_Angeles \
           --workdir /home/$USER \
           --interactive --tty \
           --entrypoint /home/$USER/.tmp_entrypoint.sh \
           ubuntu
```

Alternatively you can run the container as a daemon with ssh enabled, and then
ssh into it. Since we are mounting your host home directory as your 
container home directory you can take advantage of your .ssh/authorized_keys
and easily ssh into the host. Here are the details:

```
wget -O ~/.tmp_entrypoint.sh \
   https://raw.githubusercontent.com/gae123/sd2/master/examples/entrypoint.sh
chmod +x ~/.tmp_entrypoint.sh
docker run --name=mycontainer \
           --hostname=mycontainer \
           --detach \
           --volume $HOME:/home/$USER  \
           --env GROUP_ID=$(id -g) \
           --env USER_ID=$(id -u) \
           --env USER=$USER \
           --env SD2_EP_SSH=1 \
           --env SD2_EP_DAEMON=1 \
           --env SD2_EP_TZ=America/Los_Angeles \
           --workdir /home/$USER \
           --publish 127.0.0.1:2223:22 \
           --entrypoint /home/$USER/.tmp_entrypoint.sh \
           ubuntu
```

And here is how you ssh into it from the command line:

```
ssh -o StrictHostKeyChecking=no \
    -o "UserKnownHostsFile /dev/null" \
    -i ~/.ssh/id_rsa-2015.pub -p 2223 $USER@127.0.0.1 
```

We published the ssh port on an IP address and port on the host that is unlikely
to have been allocated but you can use any address/port you wish. 