#!/bin/bash
source ./init.sh

list=$(pgrep -f "spidercrab_slave.py")

if [ -n "$list" ]
then
    echo "Running Spidercrab slaves"
    exit 0    
fi
exit 1

