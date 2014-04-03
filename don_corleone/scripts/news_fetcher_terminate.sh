#!/bin/bash
source ./init.sh
kill `ps -ef | grep graph_worker_manager.py | grep -v grep | awk '{print $2}'`

