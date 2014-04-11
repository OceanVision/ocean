#!/bin/bash

function run_bg_job {
    echo `whoami`
    echo Running $1 $2
    #nohup sudo -o E $2 >/dev/null 2>&1 &
    rm error_logs/$1.err
    rm error_logs/$1.out
    touch error_logs/$1.err
    touch error_logs/$1.out
    nohup sudo -E $2 > error_logs/$1.out  2>  error_logs/$1.err &
#    nohup sudo -E $2
#    screen -dmSL $1 $2
}
