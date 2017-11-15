#!/bin/bash

readonly OS=$(uname)

if [[ $OS == 'Darwin' ]]; then

    # Install some custom requirements on OS X
    # e.g. brew install pyenv-virtualenv

    case "${TOXENV}" in
        py27)
            # Install some custom Python 2.7 requirements on OS X
            ;;
        py33)
            # Install some custom Python 3.3 requirements on OS X
            ;;
    esac
elif [[ $OS == 'Linux' ]]; then
    # Install some custom requirements on Linux
    sudo apt-get -y install python python-pip pylint make
    sudo apt-get -y install build-essential python-dev
else
    error
fi

sudo pip install six -U
sudo pip install jinja2
sudo pip install pyinstaller
sudo pip install pyyaml
sudo pip install python-daemon
sudo pip install jsonschema
sudo pip install pylint
sudo pip install pytest
type pyinstaller