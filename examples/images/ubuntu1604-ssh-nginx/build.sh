#!/usr/bin/env bash

set -e   # exit on first error

readonly SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sudo docker login
sudo docker build -t pako/ubuntu1604-ssh-nginx:1.0 $SCRIPTPATH
sudo docker push pako/ubuntu1604-ssh-nginx:1.0