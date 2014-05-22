#!/bin/bash
source ./init.sh

list=$(pgrep -f "odm_server.py")



if [ -n "$list" ]
then
    echo "Running lionfish"
    exit 0    
fi
exit 1

