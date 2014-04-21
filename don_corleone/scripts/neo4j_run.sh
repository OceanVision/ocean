#!/bin/bash
source ./init.sh
echo "Running Neo4j..."
sudo -E neo4j start

list=$(ps ax | grep bin/neo4j)

if [ -n "$list" ]
then
    echo "Neo4j is running"
    exit 0    
fi
exit 1

