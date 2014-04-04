#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
cmd=$2" ""${@:3}"
run_bg_job $1 "$cmd"
