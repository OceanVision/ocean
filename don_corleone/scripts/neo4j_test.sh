#!/bin/bash
source ./init.sh


list=$(ps ax | grep neo4j.*java | grep -v grep )


if [ -n "$list" ]
then
    echo "Neo4j is running"
    exit 0    
fi
exit 1

