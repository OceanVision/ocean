#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
echo "Running ODM Server"
python ../odm_server.py
