#!/bin/bash
source ./init.sh

list=$(pgrep -f "lionfish.jar")


if [ -n "$list" ]
then
    echo "Running lionfish scala server"
    exit 0    
fi
exit 1

