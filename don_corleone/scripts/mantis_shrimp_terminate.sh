#!/bin/bash
source ./init.sh
list=$(pgrep -f "mantis_shrimp.jar")

for proc in $list
do
    sudo -E kill -9 $proc
done

list=$(pgrep -f "mantis_shrimp.jar")
if [ -z "$list" ]
then
    echo "Terminating Mantis Shrimp.. OK"
    exit 0
fi
exit 1
