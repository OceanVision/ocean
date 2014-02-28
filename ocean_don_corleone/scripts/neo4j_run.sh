#!/bin/bash
source ./init.sh
source ./nohupwrapper.sh
echo `cat ocean_password` | sudo -S service neo4j-service start
