#!/usr/bin/env bash
#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

UNUSED_USER_ID=21338
UNUSED_GROUP_ID=21337

# The set_group_permissions and set_user_permissions functions come from here
# https://github.com/schmidigital/permission-fix/blob/master/LICENSE
# MIT License

function set_group_permissions() {
    readonly DOCKER_GROUP=$1
    readonly HOST_GROUP_ID=$2
    # Setting Group Permissions
    DOCKER_GROUP_CURRENT_ID=`id -g $DOCKER_GROUP`

    if [ $DOCKER_GROUP_CURRENT_ID -eq $HOST_GROUP_ID ]; then
      echo "Group $DOCKER_GROUP is already mapped to $DOCKER_GROUP_CURRENT_ID. Nice!"
    else
      echo "Check if group with ID $HOST_GROUP_ID already exists"
      DOCKER_GROUP_OLD=`getent group $HOST_GROUP_ID | cut -d: -f1`

      if [ -z "$DOCKER_GROUP_OLD" ]; then
        echo "Group ID is free. Good."
      else
        echo "Group ID is already taken by group: $DOCKER_GROUP_OLD"

        echo "Changing the ID of $DOCKER_GROUP_OLD group to $UNUSED_GROUP_ID"
        groupmod -o -g $UNUSED_GROUP_ID $DOCKER_GROUP_OLD
      fi

      #echo "Changing the ID of $DOCKER_GROUP group to $HOST_GROUP_ID"
      #groupmod -o -g $HOST_GROUP_ID $DOCKER_GROUP || true
      echo "Finished"
      echo "-- -- -- -- --"
    fi
}

function set_user_permissions() {
    readonly DOCKER_USER=$1
    readonly HOST_USER_ID=$2
    # Setting User Permissions
    DOCKER_USER_CURRENT_ID=`id -u $DOCKER_USER`

    if [ $DOCKER_USER_CURRENT_ID -eq $HOST_USER_ID ]; then
      echo "User $DOCKER_USER is already mapped to $DOCKER_USER_CURRENT_ID. Nice!"

    else
      echo "Check if user with ID $HOST_USER_ID already exists"
      DOCKER_USER_OLD=`getent passwd $HOST_USER_ID | cut -d: -f1`

      if [ -z "$DOCKER_USER_OLD" ]; then
        echo "User ID is free. Good."
      else
        echo "User ID is already taken by user: $DOCKER_USER_OLD"

        echo "Changing the ID of $DOCKER_USER_OLD to 21337"
        usermod -o -u $UNUSED_USER_ID $DOCKER_USER_OLD
      fi

      #echo "Changing the ID of $DOCKER_USER user to $HOST_USER_ID"
      #usermod -o -u $HOST_USER_ID $DOCKER_USER || true
      echo "Finished"
    fi
}

readonly DOCKER_USER_ID=$(id -u $USER)
if [ x"$DOCKER_USER_ID" = x"" ]; then
    # First time only
    set_user_permissions $USER $USER_ID
    set_group_permissions $USER $GROUP_ID
    addgroup --gid $GROUP_ID $USER
    adduser --disabled-password --no-create-home --gecos '' --uid $USER_ID --ingroup $USER $USER
fi
sleep infinity