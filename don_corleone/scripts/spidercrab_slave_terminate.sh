#!/bin/bash
source ./init.sh
list=$(pgrep -f "spidercrab_slave.py")

for proc in $list
do
    echo `cat ocean_password` | sudo -S kill -9 $proc
done

list=$(pgrep -f "spidercrab_slave.py")
if [ -z "$list" ]
then
    echo "Terminating spidercrab_slave... OK"
    exit 0
fi
exit 1
