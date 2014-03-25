#!/bin/bash
source ./init.sh
source ./run_bg_job.sh
gunicorn -c gunicorn_config.py ocean_don_corleone:app
