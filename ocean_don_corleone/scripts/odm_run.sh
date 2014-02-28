#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
run_bg_job "odm_server" "python ../odm_server.py"
