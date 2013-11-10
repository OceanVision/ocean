"""
Prototype for job fetching news.

First version support threads and workers very locally (cannot scale beyond single machine).append


TODO: In the future communicate through postgresql/reimplement in Scala
"""
import sys
import copy
sys.path.append("..")
from graph_worker import GraphWorker
import logging
from privileges import construct_full_privilege, privileges_bigger_or_equal

# Very prototypical implementation of worker/master
global_job_list = []

class NewsFetcher(GraphWorker):
    required_privileges = construct_full_privilege()

    def __init__(self, privileges, master_descriptor=None):
        if not privileges_bigger_or_equal(privileges, NewsFetcher.required_privileges):
            raise Exception("Not enough privileges")
        self.privileges = copy.deepcopy(privileges)
        if master_descriptor is None:
            self.type = "master"
        else:
            self.type = "worker"
            self.master_descriptor = master_descriptor
        pass


    def get_required_privileges(self):
        return NewsFetcher.required_privileges

    @staticmethod
    def create_master(self, **params):
        if len(params) != 1:
            raise Exception("Wrong param list")

        return NewsFetcher(**params)

    @staticmethod
    def create_worker(self, master_descriptor, **params):
        if len(params) != 1:
            raise Exception("Wrong param list")
        params["master_descriptor"] = master_descriptor
        return NewsFetcher(**params)




if __name__ == "__main__":
    print "Hello"
    pass
