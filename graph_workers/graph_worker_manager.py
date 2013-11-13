"""
Will be rewritten to database driven communication
"""
import sys,os
lib_path = os.path.abspath('./news_fetcher')
sys.path.append(lib_path)
from utils import logger
from news_fetcher import NewsFetcher
import threading
from privileges import construct_full_privilege, privileges_bigger_or_equal

class GraphWorkersManager(object):
    """
        Stub for manager of workers. On singal terminates all workers
        Will be rewritten to database driven communication
    """
    def __init__(self):
        self.graph_workers = []

    def run(self):
        # Now it will only create NewsFetcher, stub :)
        nf_master = NewsFetcher.create_master(privileges=construct_full_privilege())
        #nf_worker = NewsFetcher.create_worker(nf_master, privileges=construct_full_privilege()) - not working
        threading.Thread(target=nf_master.run).start()
        self.graph_workers.append(nf_master)

    def terminate(self):
        for gw in self.graph_workers:
            gw.terminate()
        logger.info("Terminated all graph workers")


import time
def test_2():
    gwm = GraphWorkersManager()
    gwm.run()
    time.sleep(5)
    gwm.terminate()



if __name__=="__main__":
    test_2()