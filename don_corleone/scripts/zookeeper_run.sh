#!/bin/bash
source ./init.sh
source ./run_bg_job.sh


echo "Running Zookeper"
echo `cat ocean_password` | sudo -S $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties



