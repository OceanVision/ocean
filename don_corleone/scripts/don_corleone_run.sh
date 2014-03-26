#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
gunicorn -c gunicorn_config.py don_corleone:app
