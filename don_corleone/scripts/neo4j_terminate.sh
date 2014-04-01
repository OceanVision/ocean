#!/bin/bash
source ./init.sh
echo `cat ocean_password` | sudo -S service neo4j-service stop
