#!/bin/bash
source ./init.sh
list=$(pgrep -f "lionfish.jar")

for proc in $list
do
    sudo -E kill -9 $proc
done

list=$(pgrep -f "lionfish.jar")
if [ -z "$list" ]
then
    echo "Terminating lionfish.. OK"
    exit 0
fi
exit 1
