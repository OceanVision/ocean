command = 'gunicorn'
bind = '127.0.0.1:8001'
workers = 1 # One worker because OceanMaster isnt a service at the moment.
