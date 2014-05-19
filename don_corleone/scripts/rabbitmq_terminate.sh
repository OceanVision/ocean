#!/bin/bash
source ./init.sh
list=$(pgrep -f "rabbitmq-server")

for proc in $list
do
    sudo -E kill -9 $proc
done

list=$(pgrep -f "rabbitmq-server")
if [ -z "$list" ]
then
    echo "Terminating RabbitMQ server... OK"
    exit 0
fi
exit 1
