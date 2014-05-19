#!/bin/bash
source ./init.sh


list=$(ps -ef | grep don_corleone_server:app | grep -v grep | awk '{print $2}')

echo "Terminating"
echo $list

for proc in $list
do
    echo `cat ocean_password` | sudo -S kill -9 $proc
done

list=$(ps -ef | grep don_corleone_server:app | grep -v grep | awk '{print $2}')
if [ -z "$list" ]
then
    echo "Terminating Don Corleone server... OK"
    exit 0
fi
exit 1
