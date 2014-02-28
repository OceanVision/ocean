#!/bin/bash
source ./init.sh
kill `ps -ef | grep odm_server | grep -v grep | awk '{print $2}'`

