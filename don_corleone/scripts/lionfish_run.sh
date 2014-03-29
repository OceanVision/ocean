#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
echo "Running ODM Server"
echo `cat ocean_password` | sudo -S python ../lionfish/odm_server.py
