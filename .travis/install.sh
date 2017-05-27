#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then

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
else
    # Install some custom requirements on Linux
    sudo apt-get -y install build-essential python-dev
fi

pip install jinja2
pip install pyinstaller
pip install python_hosts
pip install pyyaml
pip install jsonschema
pip install pylint