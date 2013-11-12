"""
Prototype for job fetching news.

First version support threads and workers very locally (cannot scale beyond single machine).append

News fetcher definition - Graph Worker working on sources of content, which are rss feeds :)
Currently it measns working on all NewsWebsites

Quick note (TODO: move it) about datetime in database:
d = datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE]
d = d.replace(tzinfo = timezone("GMT")) - otherwise the system won't work properly

"""

#TODO: In the future communicate through postgresql/reimplement in Scala
#TODO: Handle carefully time (UTC not GMT)

import sys
import copy
from collections import namedtuple
sys.path.append("..")
from graph_worker import GraphWorker
import logging
from neo4j_wrapper import datetime_to_pubdate, pubdate_to_datetime, get_type_metanode
from privileges import construct_full_privilege, privileges_bigger_or_equal
from py2neo import neo4j
from py2neo import node, rel
import py2neo
from graph_defines import * # import defines for fields
from utils import logger
import urllib2
import xml.dom.minidom
from datetime import timedelta, datetime
import pytz
from dateutil import parser
from pytz import timezone

NewsFetcherJob = namedtuple("NewsFetcherJob", 'neo4j_node work_time')
"""
    neo4j_node - neo4j_node where attach news
    work_time - when to pull news (as datetime)
"""


class GraphWorkersManager(object):
    """ Stub for manager of workers. On singal terminates all workers """
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


import threading
class NewsFetcher(GraphWorker):
    required_privileges = construct_full_privilege()
    minimum_time_delta_to_update = 0 #TODO: replace

    def __init__(self, privileges, master_descriptor=None):
        if not privileges_bigger_or_equal(privileges, NewsFetcher.required_privileges):
            raise Exception("Not enough privileges")

        # initialize connection. one connection per graph_worker
        self.graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        self.privileges = copy.deepcopy(privileges)
            # used for interprocess communication, simillar do CV :)
            # master sends terminate to workers and termiantes gracefully itself
        self.terminate_event = threading.Event()
        self.update_frequency_seconds = 60

        if master_descriptor is None:
            self.workers = []
            self.type = "master"
            # Very prototypical implementation of worker/master : note in the future there is ONE global job list :)
            self.global_job_list = [] # We can assume that this is "almost sorted" time-wisely
        else:
            self.type = "worker"
            self.master_descriptor = master_descriptor
        pass

    def terminate(self):
        self.terminate_event.set()

    def get_required_privileges(self):
        return NewsFetcher.required_privileges

    @staticmethod
    def create_master(**params):
        if len(params) != 1:
            raise Exception("Wrong param list")

        return NewsFetcher(**params)

    @staticmethod
    def create_worker(master_descriptor, **params):
        #TODO: Implement multithreaded news_fetcher
        raise NotImplementedError() # Single threaded for now

        if len(params) != 1:
            raise Exception("Wrong param list")
        params["master_descriptor"] = master_descriptor
        return NewsFetcher(**params)


    def process(self, job):
        news_nodes = self._fetch_news(job.neo4j_node)
        logger.info("Fetched "+str(len(news_nodes))+" from "+job.neo4j_node["link"])
        n = self._add_news_to_graph(job.neo4j_node, news_nodes)

        logger.info("Added {0} news to graph".format(n))
        # Enqueue next job
        self.global_job_list.append(NewsFetcherJob(job.neo4j_node,
            (datetime.now() + timedelta(seconds=self.update_frequency_seconds)))) #TODO: pick delta?


    def run(self):
        # Master job add jobs
        nf = self._get_all_newsfeeds()
        for n in nf:
            self.global_job_list.append(NewsFetcherJob(n,
                datetime.now()- timedelta(minutes=1)))
            #logger.info("Taking care of "+str(n))
            #list_news = fetch_news(n)
            #add_news_to_graph(n, graph_db, list_news)
            #Initialize

        logger.info(datetime.now())

        # Main loop
        while not self.terminate_event.is_set():
            if len(self.global_job_list) == 0:
                time.sleep(1) #TODO : as variable
                continue

            current_job = self.global_job_list[0]
            if current_job.work_time < datetime.now():
                current_job = self.global_job_list.pop(0) #TODO: Not very thread safe :<
                self.process(current_job)

            time.sleep(0.01) #TODO: as variable

        for worker in self.workers:
            if worker is not NewsFetcher:
                raise Exception("Wrong Worker class")
            worker.terminate_event.terminate()

        logger.info("Terminated master thread")

    def _register_worker(self):
        raise NotImplementedError()


    def _get_all_newsfeeds(self):
        """
            @returns lists of all news feeds in the system (as py2neo.node,
                note: you can refer to properties by node["property"] and
                to id by node._id :)
        """

        my_batch = neo4j.ReadBatch(self.graph_db)
        my_batch.append_cypher( # will return list of records :)
            """
            start n=node(*)
            where id(n)<>0 and HAS(n.label) and n.label = "__news_website__"
            return n;
            """
        ) #TODO: inefficient.
        news_websites = []
        logger.info("Submiting query!")
        result = my_batch.submit()
        for record in result[0]:
            news_websites.append(record.n)
        return news_websites

    def _add_news_to_graph(self, news_website, list_of_news):
        """
            @param news_website -
                node to which we will attach the news
                **note** : assumes that are sorted newer to older !!!
                **note** : news_website has to have OPEN graph_db connection,
                best option : THE SAME AS self.graph_db!! (news_website.graph_db) !!


            Adds news to graph taking care of all metadata

            @returns number of nodes added
        """

        #TODO: "<" in queries is not accepted by Cypher
        #logger.info(datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE]))
        #logger.info(datetime.fromtimestamp(time.time()))
        #last_updated = datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE])
        ##logger.info(last_updated)
        ##logger.info(time.gmtime())
        #logger.info(datetime.fromtimestamp(time.time())) #super dziala
        #d = datetime.fromtimestamp(time.time())
        #d.replace(tzinfo=timezone("GMT"))
        #logger.info(d)
        #logger.info("test")
        #logger.info(datetime.fromtimestamp(time.mktime(time.gmtime())))
        #logger.info(datetime.fromtimestamp(int(time.gmtime()), timezone("GMT")))
        last_updated = datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE])
        last_updated = last_updated.replace(tzinfo=timezone("GMT")) # Otherwise it would do a conversion -1h  (if given timezone as parameter)
        news_type_node = get_type_metanode(self.graph_db, NEWS_TYPE_MODEL_NAME) #TODO: it should be cached somewhere

        # We need this node to add HAS_INSTANCE_RELATION
        nodes_to_add = []
        for news in list_of_news:
            # !! I am assuming here GMT time !!
            # TODO: Convert everything to UTC?
            d_news = pubdate_to_datetime(news["pubdate"])
            d_news = d_news.replace(tzinfo=timezone("GMT"))


            if not (d_news > last_updated) > 0:
                break
            news["label"] = NEWS_LABEL # add metadata
            nodes_to_add.append(py2neo.node(**news)) # assume is dictionary

        if len(nodes_to_add) == 0:
            logger.warning("No nodes added")
            return 0

        last_updated_current = pubdate_to_datetime(nodes_to_add[0]["pubdate"])
        last_updated_current = last_updated_current.replace(tzinfo=timezone("GMT"))



        nodes_added = self.graph_db.create(*nodes_to_add)

        instance_relations = [py2neo.rel(news_type_node, HAS_INSTANCE_RELATION, content)
                              for content in nodes_added]
        produces_relations = [py2neo.rel(news_website, PRODUDES_RELATION, content)
                              for content in nodes_added]

        logger.info("Creating necessary metadata")
        self.graph_db.create(*instance_relations)
        logger.info("Created instance metadata relations")
        self.graph_db.create(*produces_relations)

        logger.info("Updating NewsWebsite "+str(news_website))
        news_website.update_properties(
            {
                NEWS_WEBSITE_LAST_UPDATE:
                    int(time.mktime(last_updated_current.timetuple()))
            }
        ) # using graph_db used to fetch this node!!

        logger.info("Added for instance "+unicode(nodes_added[0]["title"]))
        #logger.info(news_type_node)
        return len(nodes_added)

    #TODO: note, that this is quite slow : this is why scala is needed
    def _fetch_news(self, news_website, newer_than=None):
        """
            @param newer_than date after which stop fetching.
                Note : due to timezone awareness might be not working.
            @param news_website is a dictionary (with uri)
            @returns lists of all news of website
        """
        if news_website[NEWS_WEBSITE_RSS_TYPE] != "rss":
            raise NotImplementedError()

        rss_link = news_website[NEWS_WEBSITE_LINK]
        response = urllib2.urlopen(rss_link)

        html = response.read()
        doc = xml.dom.minidom.parseString(html)
        feed = doc.childNodes[0].getElementsByTagName("channel")[0].getElementsByTagName("item")  # <root>-><rss>-><channel>



        # Default iteration stop
        if newer_than is None:
            newer_than = datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE], timezone("GMT"))
            #newer_than.tzinfo = timezone("GMT")

        def try_get_node_value(node, value, default = u""):
            """ Note we return everything as unicode !! """
            try:
                text = ""
                childNodes = node.getElementsByTagName(value)[0].childNodes
                for child in childNodes:
                    text = child.nodeValue
                    text = text.strip()
                    if text != "": return text

                return text
            except Exception, e:
                return default

        news_nodes = []
        for id,item in enumerate(feed):
            news_node = {}
            news_node["title"] = try_get_node_value(item, "title")
            news_node["guid"] = try_get_node_value(item, "guid")
            news_node["description"] = try_get_node_value(item, "description")
            news_node["link"] = try_get_node_value(item, "link")


            d = pubdate_to_datetime(try_get_node_value(item, "pubDate"))
            d = d.replace(tzinfo=timezone("GMT"))

            if newer_than is not None:
                if d < newer_than: # check for sign
                    break
            news_node["pubdate"] = datetime_to_pubdate(d)
            news_nodes.append(news_node)

        return news_nodes





def test_1():
    """ Basic test for news_fetcher """
    nf_master = NewsFetcher.create_master(privileges=construct_full_privilege())
    #nf_worker = NewsFetcher.create_worker(nf_master, privileges=construct_full_privilege())
    threading.Thread(target=nf_master.run).start()
    time.sleep(10)
    nf_master.terminate_event.set()
    logger.info("Terminated master")
    #nf_worker.run()

def test_2():
    gwm = GraphWorkersManager()
    gwm.run()
    time.sleep(1)
    gwm.terminate()

import time

def test_list():
    print time.time()


import math
def check_if_update(news_website):
    """
        @param news_website is a dictionary (with uri)
    """
    if math.fabs(float(news_website[NEWS_WEBSITE_LAST_UPDATE]) - time.time()) > NewsFetcher.minimum_time_delta_to_update:
        return True
    else:
        return False








if __name__ == "__main__":
    test_1()
