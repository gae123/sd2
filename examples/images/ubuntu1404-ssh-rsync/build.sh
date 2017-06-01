#!/usr/bin/env bash

set -e   # exit on first error

readonly REPO=ubuntu1404-ssh-rsync
readonly TAG=1.0

readonly SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#sudo docker login
sudo docker build -t pako/$REPO:$TAG $SCRIPTPATH
sudo docker push pako/$REPO:$TAG