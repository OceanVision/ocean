#!/bin/bash
source ./init.sh
echo `cat ocean_password` | sudo -S neo4j start
