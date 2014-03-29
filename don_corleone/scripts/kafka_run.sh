#!/bin/bash
source ./init.sh
source ./run_bg_job.sh


echo "Running Kafka Broker"
echo `cat ocean_password` | sudo -S $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties



