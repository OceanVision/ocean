#!/bin/sh
list=$(pgrep -f "spidercrab_slaves.py")

for proc in $list
do
    sudo kill -9 $proc
done

if [ "${#list[@]}" -gt 0 ]
then
    echo "Terminating Spidercrab slaves... OK"
fi

