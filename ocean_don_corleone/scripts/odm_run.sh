#!/bin/bash
screen -q
source ./init.sh
python ../odm_server.py &
screen -d
