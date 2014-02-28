#!/bin/bash

function run_bg_job {
    echo $1
    (nohup $1 > foo.out 2> foo.err < /dev/null) &
}
