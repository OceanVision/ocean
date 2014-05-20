#!/bin/bash
source ./init.sh

list=$(pgrep -f "rabbitmq-server")


if [ -n "$list" ]
then
    echo "Running RabbitMQ"
    exit 0    
fi
exit 1

