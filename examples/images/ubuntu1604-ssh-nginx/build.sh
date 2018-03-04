#!/usr/bin/env bash

set -e   # exit on first error

readonly REPO=ubuntu1604-ssh-nginx
readonly TAG=1.2

readonly SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#sudo docker login
sudo docker build -t pako/$REPO:$TAG $SCRIPTPATH
sudo docker push pako/$REPO:$TAG