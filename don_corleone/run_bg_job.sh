#!/bin/bash

function run_bg_job {
    echo Running $1 $2
    nohup $2 >/dev/null 2>&1 &
#    nohup $2
#    screen -dmSL $1 $2
}
