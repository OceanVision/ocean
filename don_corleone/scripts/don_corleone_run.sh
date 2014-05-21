#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
#sudo -E python don_corleone_server.p
gunicorn -c gunicorn_config.py don_corleone_server:app
