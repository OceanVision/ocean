command = 'gunicorn'
bind = '127.0.0.1:8881'
workers = 1 # One worker because OceanMaster isnt a service at the moment.
