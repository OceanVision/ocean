#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
source ~/.bashrc

echo "Running Kafka Broker"
sudo -E $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties



