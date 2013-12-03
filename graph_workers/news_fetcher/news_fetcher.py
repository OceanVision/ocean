"""
Prototype for job fetching news.

First version support threads and workers very locally (cannot scale beyond single machine).append

News fetcher definition - Graph Worker working on sources of content, which are rss feeds :)
Currently it measns working on all NewsWebsites

Quick note (TODO: move it) about datetime in database:
d = datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE]
d = d.replace(tzinfo = timezone("GMT")) - otherwise the system won't work properly
"""

#TODO: Add careful tests (added news difference etc.)
#TODO: In the future communicate through postgresql/reimplement in Scala
#TODO: Add levels to logger (in std it is present)
#TODO: Handle carefully time (UTC not GMT)

import sys
import copy
from collections import namedtuple
sys.path.append("..")
import inspect

from graph_worker import GraphWorker
import logging
from neo4j_wrapper import datetime_to_pubdate, pubdate_to_datetime, get_type_metanode, count_same_news, get_records_from_cypher
from privileges import construct_full_privilege, privileges_bigger_or_equal
from py2neo import neo4j
from py2neo import node, rel
import py2neo
from graph_defines import * # import defines for fields
from utils import *

import urllib2
import xml.dom.minidom
from datetime import timedelta, datetime
from dateutil import parser
import time
from pytz import timezone

NewsFetcherJob = namedtuple("NewsFetcherJob", 'neo4j_node work_time')
"""
    neo4j_node - neo4j_node where attach news
    work_time - when to pull news (as datetime)
"""

#TODO: implement logger with logging level.



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
        self.update_frequency_seconds = 10
        self.update_frequency_news_channels = 10


        if master_descriptor is None:
            self.workers = []
            self.type = "master"
            # Very prototypical implementation of worker/master : note in the future there is ONE global job list :)
            self.global_job_list = [] # We can assume that this is "almost sorted" time-wisely
        else:
            self.type = "worker"
            self.master_descriptor = master_descriptor
        pass



    def process(self, job):
        news_nodes = self._fetch_news(job.neo4j_node)
        logger.info("Fetched "+str(len(news_nodes))+" from "+job.neo4j_node["link"])
        n = self._add_news_to_graph(job.neo4j_node, news_nodes)

        logger.info("Added {0} news to graph".format(n))
#         # Enqueue next job
#         self.global_job_list.append(NewsFetcherJob(job.neo4j_node,
#             (datetime.now() + timedelta(seconds=self.update_frequency_seconds))))


    def run(self):
        # Master job add jobs
        nf = self._get_all_newsfeeds()
        for n in nf:
            self.global_job_list.append(NewsFetcherJob(n,
                datetime.now()- timedelta(minutes=1)))

        logger.info("Scanning " +str(len(nf))+ " news_website")


        # Main loop
        time_elapsed = 0
        while not self.terminate_event.is_set():
            if len(self.global_job_list) == 0: #Not that frequent
                nf = self._get_all_newsfeeds()
                for n in nf:
                    self.global_job_list.append(NewsFetcherJob(n, datetime.now()- timedelta(minutes=1)))
                logger.info("Updated global_job_list to "+str(len(self.global_job_list)))
                time.sleep(1)


            current_job = self.global_job_list[0]
            if current_job.work_time < datetime.now():
                current_job = self.global_job_list.pop(0) #TODO: Not very thread safe :<
                self.process(current_job)
            
            time.sleep(0.1) #TODO: as variable
            time_elapsed += 1

#             cont = raw_input("continue?")


        for worker in self.workers:
            if worker is not NewsFetcher:
                raise Exception("Wrong Worker class")
            worker.terminate_event.terminate()

        logger.info("Terminated master thread")

    def _register_worker(self):
        raise NotImplementedError()


    #TODO: move to neo4j_wrapper to get_all_instances()
    def _get_all_newsfeeds(self):
        """
            @returns lists of all news feeds in the system (as py2neo.node,
                note: you can refer to properties by node["property"] and
                to id by node._id :)

                if there were no needed fields, they are added :)
        """
        query = \
        """
        start n=node(*)
        where id(n)<>0 and HAS(n.label) and n.label = "__news_website__"
        return n, count(n);
        """

        news_websites = []
        records = get_records_from_cypher(self.graph_db, query)
        if records is None:
            logger.error("Error while communicating with neo4j database. No news websites fetched")
            exit(1)

        for record in get_records_from_cypher(self.graph_db, query):
            news_websites.append(record.n)
            if NEWS_WEBSITE_LAST_UPDATE not in news_websites[-1]:
                logger.info("Adding last_updated field to "+unicode(news_websites[-1]))
                news_websites[-1][NEWS_WEBSITE_LAST_UPDATE] = 0

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


        last_updated = database_timestamp_to_datetime(news_website[NEWS_WEBSITE_LAST_UPDATE])

        logger.info("Last updated news_website is "+str(last_updated))

        news_type_node = get_type_metanode(self.graph_db, NEWS_TYPE_MODEL_NAME) #TODO: it should be cached somewhere

        # We need this node to add HAS_INSTANCE_RELATION
        nodes_to_add = []
        for news in list_of_news:
            d_news = pubdate_to_datetime(news["pubdate"])
            logger.info(d_news)
            logger.info(last_updated)
            if (d_news > last_updated): #not always sorted!
                news["label"] = NEWS_LABEL # add metadata
                nodes_to_add.append(py2neo.node(**news)) # assume is dictionary

        if len(nodes_to_add) == 0:
            logger.warning("No nodes added")
            return 0

        last_updated_current = pubdate_to_datetime(nodes_to_add[0]["pubdate"])
        news_website.update_properties(
            {
                NEWS_WEBSITE_LAST_UPDATE:
                    GMTdatetime_to_database_timestamp(last_updated_current)
            }
        ) # using graph_db used to fetch this node!!


        #Check here for news[0] if it is in the database

        existing_nodes = count_same_news(self.graph_db, news_website, nodes_to_add[0]["title"])

        if existing_nodes > 0:
            logger.warning("")
            logger.warning(nodes_to_add[0])
            logger.warning(existing_nodes)
            logger.warning("Existing nodes ! Probably something wrong with "+unicode(news_website))
            return 0

        logger.info("Updating news_website last_updated to "+str(last_updated_current))

        nodes_added = self.graph_db.create(*nodes_to_add)

        instance_relations = [py2neo.rel(news_type_node, HAS_INSTANCE_RELATION, content)
                              for content in nodes_added]
        produces_relations = [py2neo.rel(news_website, PRODUDES_RELATION, content)
                              for content in nodes_added]

        logger.info("Creating necessary metadata")
        self.graph_db.create(*instance_relations)
        logger.info("Created instance metadata relations")
        self.graph_db.create(*produces_relations)

        logger.info("Updating NewsWebsite "+unicode(news_website))
        logger.info("Added for instance "+unicode(nodes_added[0]["title"]))
        #logger.info(news_type_node)
        return len(nodes_added)


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
            newer_than = database_timestamp_to_datetime(news_website[NEWS_WEBSITE_LAST_UPDATE])

        logger.info("Fetching news from "+str(rss_link)+" newer_than "+str(newer_than))


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
            news_node["title"] = unicode(try_get_node_value(item, "title")) #unicode() because it is already encoded!
            news_node["guid"] = unicode(try_get_node_value(item, "guid"))
            news_node["description"] = unicode(try_get_node_value(item, "description"))
            news_node["link"] = unicode(try_get_node_value(item, "link"))


            d = pubdate_to_datetime(try_get_node_value(item, "pubDate"))
            if newer_than is None or d > newer_than: # Not sorted :(
                    news_node["pubdate"] = datetime_to_pubdate(d)
                    news_nodes.append(news_node)

        return news_nodes

    def terminate(self):
        self.terminate_event.set()

    def get_required_privileges(self):
        return NewsFetcher.required_privileges

    @staticmethod
    def create_master(**params):
        logger.info("Created news_fetcher master")
        logger.info((inspect.stack()[1],inspect.getmodule(inspect.stack()[1][0])))
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





#def test_1():
#    """ Basic test for news_fetcher """
#    nf_master = NewsFetcher.create_master(privileges=construct_full_privilege())
#    #nf_worker = NewsFetcher.create_worker(nf_master, privileges=construct_full_privilege())
#    threading.Thread(target=nf_master.run).start()
#    time.sleep(10)
#    nf_master.terminate_event.set()
#    logger.info("Terminated master")
#    #nf_worker.run()
#
#
#
#import time
#
#def test_list():
#    print time.time()
#
#
#import math
#def check_if_update(news_website):
#    """
#        @param news_website is a dictionary (with uri)
#    """
#    if math.fabs(float(news_website[NEWS_WEBSITE_LAST_UPDATE]) - time.time()) > NewsFetcher.minimum_time_delta_to_update:
#        return True
#    else:
#        return False
#
#


