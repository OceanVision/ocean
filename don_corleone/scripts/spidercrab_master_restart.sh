#!/bin/sh
list=$(pgrep -f "spidercrab_master.py")

for proc in $list
do
    sudo kill -9 $proc
done

if [ "${#list[@]}" -gt 0 ]
then
    echo "Terminating Spidercrab master... OK"
fi

