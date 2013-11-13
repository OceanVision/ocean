#!/usr/bin/python
"""
Runs manage.py runserver and all other needed services
"""
from signal import *
import sys, time
import threading
import sys, os

# Add module
sys.path.append(os.path.abspath('../graph_workers'))
sys.path.append(os.path.abspath('../graph_workers/news_fetcher'))
from graph_worker_manager import GraphWorkersManager
from utils import logger

#TODO: is this the best place to put iy?
gwm = None

def run_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocean.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver"])

def clean(*args):
    logger.info("Terminating GWM")
    gwm.terminate()
    exit(0)


if __name__ == "__main__":
    global gwm
    gwm = GraphWorkersManager()

    for sig in (SIGINT,):
        signal(sig, clean)

    t1=threading.Thread(gwm.run())
    t1.daemon = True
    t2=threading.Thread(target=run_django)
    t2.daemon = True

    # When no daemon threads are left , program terminates

    t1.start()
    t2.start()

    while True: # making catching possible..
        time.sleep(0.1)