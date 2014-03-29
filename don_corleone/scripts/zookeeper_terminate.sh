#!/bin/bash
source ./init.sh

echo "Stopping Zookeper"
echo `cat ocean_password` | sudo -S $KAFKA_HOME/bin/zookeeper-server-stop.sh 



