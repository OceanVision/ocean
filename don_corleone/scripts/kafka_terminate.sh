#!/bin/bash
source ./init.sh


echo 'Terminating zookeper stop'
echo `cat ocean_password` | sudo -S $KAFKA_HOME/bin/zookeper-server-stop.sh





list=$(ps -ef | grep kafka_2 | grep -v grep | awk '{print $2}')

echo "Terminating"
echo $list

for proc in $list
do
    echo `cat ocean_password` | sudo -S kill -9 $proc
done

list=$(ps -ef | grep kafka_2 | grep -v grep | awk '{print $2}')
if [ -z "$list" ]
then
    echo "Terminating Kafka server... OK"
    exit 0
fi
exit 1
