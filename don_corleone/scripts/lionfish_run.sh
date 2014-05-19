#!/bin/bash
source ./init.sh
echo "Running ODM Server"

sudo -E python2 ../lionfish/python_lionfish/server/odm_server.py ${@:1}


