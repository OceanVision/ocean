#!/bin/bash
source ./init.sh
source ./run_bg_job.shE
source ~/.bashrc

echo "Running Zookeper"
sudo -E $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties



