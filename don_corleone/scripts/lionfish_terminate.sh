#!/bin/bash
source ./init.sh
list=$(pgrep -f "odm_server.py")

for proc in $list
do
    echo `cat ocean_password` | sudo -S kill -9 $proc
done

list=$(pgrep -f "odm_server.py")
if [ -z "$list" ]
then
    echo "Terminating Lionfish server... OK"
    exit 0
fi
exit 1
