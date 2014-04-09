#!/bin/bash
source ./init.sh
list=$(ps -ef | grep kafka_2 | grep -v grep | awk '{print $2}')

if [ -n "$list" ]
then
    echo "Kafka running .."
    exit 0
fi
exit 1
