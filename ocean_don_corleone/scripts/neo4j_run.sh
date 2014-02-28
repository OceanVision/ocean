#!/bin/bash

./init.sh
echo `cat ocean_password` | sudo -S service neo4j-service start
