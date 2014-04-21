#!/bin/bash
source ./init.sh
echo "Running Spidercrab master"
sudo -E python2 ../graph_workers/spidercrab_master.py
