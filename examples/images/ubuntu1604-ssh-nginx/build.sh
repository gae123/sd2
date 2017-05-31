#!/usr/bin/env bash

set -e   # exit on first error

VERSION=1.1

readonly SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#sudo docker login
sudo docker build -t pako/ubuntu1604-ssh-nginx:$VERSION $SCRIPTPATH
sudo docker push pako/ubuntu1604-ssh-nginx:$VERSION