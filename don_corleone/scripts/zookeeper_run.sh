#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
source ~/.bashrc

echo "Running Zookeper"
sudo -E $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties



