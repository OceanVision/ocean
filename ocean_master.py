""" This is a prototype for OceanMaster object.

We will se how it works in practice and modify it in an agile way
"""


import sys
import os
import logging


sys.path.append(os.path.join(os.path.dirname(__file__), "graph_views"))
sys.path.append(os.path.join(os.path.dirname(__file__), "graph_workers"))
sys.path.append(os.path.join(os.path.dirname(__file__), "graph_workers/news_fetcher"))

import graph_view
import graph_worker_manager
from utils import deep_eq_wrapper, deep_eq
from utils import *

import time
import threading
import datetime

logging.basicConfig(level=MY_DEBUG_LEVEL)
ologger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
ologger.addHandler(ch)
ologger.propagate = False
ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),"logs/ocean_master.log"), )
ch_file.setFormatter(formatter)
ch_file.setLevel(MY_IMPORTANT_LEVEL)
ologger.addHandler(ch_file)



class OceanMaster(object):
    """ Ocean master - every important call should go through this object

    """
    def __init__(self):
        ologger.log(MY_IMPORTANT_LEVEL, "Created OceanMaster")
        self.graph_views = []
        self.graph_views_dict = {}  # Keeping deep_eq_wrapper inside
        self.update_frequency = 100  # Every 1s check if GraphView should be updated
        self.terminate_event = threading.Event()

    def terminate(self):
        ologger.log(MY_IMPORTANT_LEVEL, "Terminating OceanMaster daemon")
        self.terminate_event.set()


    def run(self):
        t = threading.Thread(target=self._run)
        t.daemon = True
        t.start()

    def _run(self):
        """
            Main loop for OceanMaster
            Worker that iterates over all graph views and updates them
        """
        ologger.log(MY_IMPORTANT_LEVEL, "Running OceanMaster daemon")
        while not self.terminate_event.is_set():
            for id, gv, last_updated in enumerate(self.graph_views):
                if last_updated - datetime.now() > datetime.timedelta(seconds=gv.update_frequency):
                    print "Updating ",gv, "last_updated=",last_updated,"now=",datetime.now()
                    self.graph_views[id][1] = datetime.now()
                    gv.update()
            time.sleep(self.update_frequency/1000.0)



    def construct_graph_view(self, graph_view_expression):
        """
        Checks in cache if this graph_view is already constructed.

        @note For now assume graph_view_expression as (Class, args, dict_args)

        If not it constructs it using graph_view_expression
        """

        # There is a bit of magic here. Deep eq wrapper allows for
        # deep comparison. It keeps its object in .v

        # TODO: rewrite to object GraphViewExpression..

        #1. Check cache
        if deep_eq_wrapper(graph_view_expression) in self.graph_views_dict:
            ologger.log(MY_IMPORTANT_LEVEL, "Found in cache: "+str(graph_view_expression) )
            return self.graph_views_dict[deep_eq_wrapper(graph_view_expression)]
        #2. If not present - construct
        else:
            ologger.log(MY_IMPORTANT_LEVEL, "Constructing "+str(graph_view_expression) )

            if len(graph_view_expression) < 3:
                ologger.log(MY_CRITICAL_LEVEL, "Wrong length of the graph_view_expression")
                return None

            constructed_gv = graph_view_expression[0](*graph_view_expression[1], **graph_view_expression[2])
            self.graph_views_dict[deep_eq_wrapper(graph_view_expression)] = constructed_gv
            return constructed_gv
        pass

    def get_content(self, graph_view_expression, graph_display_expression):
        """

        Get content (igraph) based on expressions
        for GraphView and GraphDisplay.

        @note: The ultimate goal is to define a language over GraphViews and GraphDisplays
        based on JSON. It is a good idea in my opinion

        @param graph_view_expression Graph View expression
        @param graph_display_expression Graph Display expression
        """
        #1. Construct graph display
        #2. Construct graph view
        #3. Check if the returning type is ok for graph display
        pass

#
##OC..
OC = None
#
#
#def test1():
#    OC.run()
#
#    gv = OC.construct_graph_view((graph_view.TestingGV, [1,2,[1,3]], {}))
#    gv2 = OC.construct_graph_view((graph_view.TestingGV, [1,2,[1,3]], {}))
#
#    print gv == gv2
#
#    time.sleep(10)
#    OC.terminate()
#
#import time
#if __name__ == "__main__":
#    OC = OceanMaster()
#    OC.run()
#
#    gv = OC.construct_graph_view((graph_view.TestingGV, [1,2,[1,3]], {}))
#    gv2 = OC.construct_graph_view((graph_view.TestingGV, [1,2,[1,3]], {}))
#
#    print gv == gv2
#
#    time.sleep(10)
#    OC.terminate()
#

