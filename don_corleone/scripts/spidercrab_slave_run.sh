#!/bin/bash
source ./init.sh
echo "Running Spidercrab slaves"
sudo -E python2 ../graph_workers/spidercrab_slaves.py
