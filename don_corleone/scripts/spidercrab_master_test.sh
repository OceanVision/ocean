#!/bin/bash
source ./init.sh

list=$(pgrep -f "spidercrab_master.py")

if [ -n "$list" ]
then
    echo "Running Spidercrab master"
    exit 0    
fi
exit 1

