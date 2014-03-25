#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
python ../graph_workers/graph_worker_manager.py
