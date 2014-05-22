#!/bin/bash
source ./init.sh
list=$(pgrep -f "logstash")

for proc in $list
do
    sudo -E kill -9 $proc
done

list=$(pgrep -f "logstash")
if [ -z "$list" ]
then
    echo "Terminating logstash... OK"
    exit 0
fi
exit 1
