"""
Will be rewritten to database driven communication
"""
print __file__

from news_fetcher import NewsFetcher
import threading
from privileges import construct_full_privilege
from signal import *
from graph_workers.graph_utils import *


class GraphWorkersManager(object):
    """
        Stub for manager of workers. On signal terminates all workers
        Will be rewritten to database driven communication
    """
    def __init__(self):
        self.graph_workers = []

    def run(self):
        # Now it will only create NewsFetcher, stub :)
        nf_master = NewsFetcher.create_master(
            privileges=construct_full_privilege())

        threading.Thread(target=nf_master.run).start()
        self.graph_workers.append(nf_master)

    def terminate(self):
        for gw in self.graph_workers:
            gw.terminate()
        logger.log(MY_INFO_IMPORTANT_LEVEL, "Terminated all graph workers")


gwm = None


def clean(*args):
    global gwm
    logger.log(MY_INFO_IMPORTANT_LEVEL, "Terminating GWM")
    gwm.terminate()
    exit(0)

if __name__ == "__main__":
    logger.log(MY_INFO_IMPORTANT_LEVEL,
               "Starting GraphWorkersManager. To be started from OceanMaster")
    gwm = GraphWorkersManager()
    gwm.run()

    for sig in (SIGINT,):
        signal(sig, clean)

    while True:
        time.sleep(1.0)

