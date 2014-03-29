#!/bin/bash
source ./init.sh
source ~/.bashrc



echo $KAFKA_HOME
echo "Stopping Zookeper"

list=$(ps -ef | grep zookeeper-server-start | grep -v grep | awk '{print $2}')

echo "Terminating"
echo $list

for proc in $list
do
    echo `cat ocean_password` | sudo -S kill -9 $proc
done



list=$(ps -ef | grep zookeeper-server-start | grep -v grep | awk '{print $2}')

if [ -z "$list" ]
then
    echo "Zookeeper terminated successfuly .."
    exit 0
fi
exit 1


