#!/bin/sh
list=$(pgrep -f "odm_server.py")

for proc in $list
do
    sudo kill -9 $proc
done

if [ "${#list[@]}" -gt 0 ]
then
    echo "Terminating Lionfish server... OK"
fi

