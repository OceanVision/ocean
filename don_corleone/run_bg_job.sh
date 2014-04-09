#!/bin/bash

function run_bg_job {
    echo `whoami`
    echo Running $1 $2
    nohup sudo -E $2 >/dev/null 2>&1 &
#    nohup sudo -E $2
#    screen -dmSL $1 $2
}
