#!/usr/bin/env bash

# Just output the files in $TESTDIR and exit

export SCRIPT_PATH=$(cd "$(dirname "${BASH_SOURCE}")"; pwd)

export SD2_CONFIG_DIR=$SCRIPT_PATH
export TESTDIR=/tmp/test-sd2-config-sshgenconfig
rm -rf $TESTDIR
mkdir -p $TESTDIR
export SD2_ETC_HOSTS=$TESTDIR/etc_hosts
export SD2_SSH_CONFIG=$TESTDIR/ssh_config
export SD2_CIDR_DB_PATH=$TESTDIR/sd2-cidr-db

sd2 
sd2 halt