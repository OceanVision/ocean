#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
run_bg_job "gwm" "python ../graph_worker_manager.py"
