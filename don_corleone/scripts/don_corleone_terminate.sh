#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
echo `ps -ef | grep don_corleone | grep -v grep | awk '{print $2}'`
kill `ps -ef | grep don_corleone | grep -v grep | awk '{print $2}'`
