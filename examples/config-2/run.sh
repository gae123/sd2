#!/usr/bin/env bash

# Just output the files in $TESTDIR and exit

export SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE}")"; pwd)

export SD2_CONFIG_DIR=$SCRIPT_PATH
export TESTDIR=/tmp/test-sd2-config-2
mkdir -p $TESTDIR
export SD2_ETC_HOSTS=$TESTDIR/etc_hosts
touch $SD2_ETC_HOSTS
export SD2_SSH_CONFIG=$TESTDIR/ssh_config
export SD2_CIDR_DB_PATH=$TESTDIR/sd2-cidr-db

sd2
echo Use \'s2 halt\' to stop the daemon
echo Use \'ssh -F $SD2_SSH_CONFIG paros-1\'