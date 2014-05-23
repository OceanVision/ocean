#!/bin/bash
source ./init.sh

list=$(pgrep -f "mantis_shrimp.jar")


if [ -n "$list" ]
then
    echo "Running mantis_shrimp scala server"
    exit 0
fi
exit 1

