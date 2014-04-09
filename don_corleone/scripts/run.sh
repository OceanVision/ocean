#!/bin/bash
source ./init.sh
cmd=$2" ""${@:3}"
sudo -E /bin/bash -c -- "source ./run_bg_job.sh && run_bg_job $1 \"$cmd\""
