#!/bin/bash
source ./init.sh
list=$(ps -ef | grep zookeeper-server-start | grep -v grep | awk '{print $2}')

if [ -n "$list" ]
then
    echo "Zookeeper running .."
    exit 0
fi
exit 1
