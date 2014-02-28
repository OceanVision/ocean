#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
run_bg_job "python ../odm_server.py"
