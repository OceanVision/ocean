#!/bin/bash
source ./init.sh

list=$(pgrep -f "spidercrab_slaves.py")

if [ -n "$list" ]
then
    echo "Running Spidercrab slaves"
    exit 0    
fi
exit 1

