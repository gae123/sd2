#!/bin/bash

readonly OS=$(uname)

if [[ $OS == 'Darwin' ]]; then

    # Install some custom requirements on OS X
    # e.g. brew install pyenv-virtualenv
    PIP=pip2
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
    PIP=pip
else
    error
fi

sudo $PIP install six -U
sudo $PIP install jinja2
sudo $PIP install pyinstaller
sudo $PIP install pyyaml
sudo $PIP install python-daemon
sudo $PIP install jsonschema==2.6.0
sudo $PIP install pylint
sudo $PIP install pytest
type pyinstaller