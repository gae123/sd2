#!/usr/bin/env bash
#############################################################################
# Copyright (c) 2017-2018 SiteWare Corp. All right reserved
#############################################################################

UNUSED_USER_ID=21338
UNUSED_GROUP_ID=21337

# Find the package manager, Ubunut uses apt-get, AML uses yum
(type apt-get &> /dev/null) && DOCKER_PKGUPD="apt-get -y update"
(type apt-get &> /dev/null) && DOCKER_PKGMGR="apt-get -y install"
(type yum &> /dev/null) && DOCKER_PKGUPD="true"
(type yum &> /dev/null) && DOCKER_PKGMGR="yum -y install"

# The set_group_permissions and set_user_permissions functions come from here
# https://github.com/schmidigital/permission-fix/blob/master/LICENSE
# MIT License

function set_group_permissions() {
    readonly DOCKER_GROUP=$1
    readonly HOST_GROUP_ID=$2
    # Setting Group Permissions
    DOCKER_GROUP_CURRENT_ID=$(id -g $DOCKER_GROUP 2> /dev/null)

    echo SGP: DG:$DOCKER_GROUP   HGID:$HOST_GROUP_ID DGCID:$DOCKER_GROUP_CURRENT_ID > /dev/null

    if [ x"$DOCKER_GROUP_CURRENT_ID" = x"$HOST_GROUP_ID" ]; then
      echo "Group $DOCKER_GROUP is already mapped to $DOCKER_GROUP_CURRENT_ID. Nice!" > /dev/null
    else
      echo "Check if group with ID $HOST_GROUP_ID already exists" > /dev/null
      DOCKER_GROUP_OLD=`getent group $HOST_GROUP_ID | cut -d: -f1`

      if [ -z "$DOCKER_GROUP_OLD" ]; then
        echo "Group ID is free. Good." > /dev/null
      else
        echo "Group ID is already taken by group: $DOCKER_GROUP_OLD" > /dev/null

        echo "Changing the ID of $DOCKER_GROUP_OLD group to $UNUSED_GROUP_ID" > /dev/null
        groupmod -o -g $UNUSED_GROUP_ID $DOCKER_GROUP_OLD
      fi

      #echo "Changing the ID of $DOCKER_GROUP group to $HOST_GROUP_ID"
      #groupmod -o -g $HOST_GROUP_ID $DOCKER_GROUP || true
      echo "Finished" > /dev/null
      echo "-- -- -- -- --" > /dev/null
    fi
}

function set_user_permissions() {
    readonly DOCKER_USER=$1
    readonly HOST_USER_ID=$2
    # Setting User Permissions
    DOCKER_USER_CURRENT_ID=$(id -u $DOCKER_USER 2> /dev/null)

    echo DU:$DOCKER_USER  HUID:$HOST_USER_ID DUCID:$DOCKER_USER_CURRENT_ID > /dev/null

    if [ x"$DOCKER_USER_CURRENT_ID" = x"$HOST_USER_ID" ]; then
      echo "User $DOCKER_USER is already mapped to $DOCKER_USER_CURRENT_ID. Nice!" > /dev/null
    else
      echo "Check if user with ID $HOST_USER_ID already exists" > /dev/null
      DOCKER_USER_OLD=`getent passwd $HOST_USER_ID | cut -d: -f1`

      if [ -z "$DOCKER_USER_OLD" ]; then
        echo "User ID is free. Good." > /dev/null
      else
        echo "User ID is already taken by user: $DOCKER_USER_OLD" > /dev/null

        echo "Changing the ID of $DOCKER_USER_OLD to 21337" > /dev/null
        usermod -o -u $UNUSED_USER_ID $DOCKER_USER_OLD
      fi

      #echo "Changing the ID of $DOCKER_USER user to $HOST_USER_ID"
      #usermod -o -u $HOST_USER_ID $DOCKER_USER || true
      echo "Finished" > /dev/null
    fi
}

# Variables that must be defined
if [ "$USER" = "" ] ; then
   echo Error: USER is not defined
   exit 1
fi
if [ "$USER_ID" = "" ] ; then
   echo Error: USER_ID is not defined
   exit 1
fi
if [ "$GROUP_ID" = "" ] ; then
   echo Error: GROUP_ID is not defined
   exit 1
fi

readonly DOCKER_USER_ID=$(id -u $USER 2> /dev/null)
if [ x"$DOCKER_USER_ID" = x"" ]; then
    (type yum &> /dev/null) && $DOCKER_PKGMGR shadow-utils  # for usermod etc
    (type sudo &> /dev/null) || ($DOCKER_PKGUPD && $DOCKER_PKGMGR sudo)
    # First time only
    set_user_permissions $USER $USER_ID
    set_group_permissions $USER $GROUP_ID
    (type yum &> /dev/null) && groupadd --gid $GROUP_ID $USER
    (type apt-get &> /dev/null) && addgroup --gid $GROUP_ID $USER
    (type yum &> /dev/null) && adduser \
                --no-create-home  --uid $USER_ID --gid $GROUP_ID $USER
    (type apt-get &> /dev/null) && adduser  \
            --disabled-password \
            --no-create-home \
            --gecos '' \
            --uid $USER_ID \
            --ingroup $USER $USER
    echo "$USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER
    if [ x"$SD2_EP_SSH" = x"1" ]; then
        (type sshd &> /dev/null) || ($DOCKER_PKGUPD && $DOCKER_PKGMGR openssh-server)
    fi
fi
if [ x"$SD2_EP_SSH" = x"1" ]; then
    service ssh start
fi
if [ -n "$SD2_EP_TZ" ] ; then
    export TZ=$SD2_EP_TZ
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
    echo $TZ > /etc/timezone
fi
[ -n "$SD2_EP_SCRIPT" ] && $SD2_EP_SCRIPT
if [ x"$SD2_EP_SHELL" = x"1" ]; then
    #su - $USER
    sudo -i -u $USER
else
    sleep infinity
fi


