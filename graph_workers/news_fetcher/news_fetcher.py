"""
Prototype for job fetching news

First version support threads and workers very locally (cannot scale beyond single machine)

News fetcher definition - Graph Worker working on sources of content, which are rss feeds :)
Currently it measns working on all ContentSources

Quick note (TODO: move it) about datetime in database:
d = datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE]
d = d.replace(tzinfo = timezone("GMT")) - otherwise the system won't work properly
"""

#TODO: Add careful tests (added news difference etc.)
#TODO: In the future communicate through postgresql/reimplement in Scala
#TODO: Add levels to logger (in std it is present)
#TODO: Handle carefully time (UTC not GMT)

import sys
import os
import copy
from collections import namedtuple
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
import inspect

from odm_client import ODMClient

from graph_worker import GraphWorker
import logging
from neo4j_wrapper import datetime_to_pubdate, pubdate_to_datetime, \
    get_all_instances, get_type_metanode, count_same_news, get_records_from_cypher
from privileges import construct_full_privilege, privileges_bigger_or_equal
from py2neo import neo4j
from py2neo import node, rel
import py2neo
from graph_defines import * # import defines for fields
from graph_utils import *
import os
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


logging.basicConfig(level=MY_DEBUG_LEVEL)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),"../../logs/news_fetcher.log"), )
ch_file.setLevel(MY_IMPORTANT_LEVEL)
logger.addHandler(ch_file)


import threading
class NewsFetcher(GraphWorker):
    required_privileges = construct_full_privilege()
    minimum_time_delta_to_update = 0

    def __init__(self, privileges, master_descriptor=None):
        if not privileges_bigger_or_equal(privileges, NewsFetcher.required_privileges):
            raise Exception("Not enough privileges")

        self.odm_client = ODMClient()
        logger.log(MY_INFO_LEVEL, "Conneting to ODM Service")
        self.odm_client.connect()

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
        """
        Process job
        @param job is a dictionary with field neo4j_node
        """
        news_nodes = self._fetch_news(job.neo4j_node)
        logger.log(MY_DEBUG_LEVEL, "Fetched "+str(len(news_nodes))+" from "+job.neo4j_node["link"])
        n = self._add_news_to_graph(job.neo4j_node, news_nodes)
        if n > 0: logger.log(MY_INFO_IMPORTANT_LEVEL, "Added {0} news to graph".format(n))



    def run(self):
        # Main loop
        time_elapsed = 0
        while not self.terminate_event.is_set():
            if len(self.global_job_list) == 0: #Not that frequent
                nf = self._get_all_newsfeeds()
                for n in nf:
                    self.global_job_list.append(NewsFetcherJob(n, datetime.now() - timedelta(minutes=1)))
                logger.log(MY_INFO_LEVEL, "Updated global_job_list to "+str(len(self.global_job_list)))
                time.sleep(1)

            current_job = self.global_job_list[0]
            if current_job.work_time < datetime.now():
                current_job = self.global_job_list.pop(0) #TODO: Not very thread safe :<
                self.process(current_job)

            time.sleep(0.1) #TODO: as variable
            time_elapsed += 1

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
        rss_content_sources = []
        for n in self.odm_client.get_all_instances(model_name=CONTENT_SOURCE_TYPE_MODEL_NAME):
            if n[CONTENT_SOURCE_RSS_TYPE] == "rss":
                rss_content_sources.append(n)
                if CONTENT_SOURCE_LAST_UPDATE not in rss_content_sources[-1]:
                    logger.log(MY_DEBUG_LEVEL, "Adding last_updated field to "+unicode(rss_content_sources[-1]))
                    rss_content_sources[-1][CONTENT_SOURCE_LAST_UPDATE] = 0

        return rss_content_sources

    def _add_news_to_graph(self, news_website, list_of_news):
        """
            @param news_website -
                node to which we will attach the news
            Adds news to graph taking care of all metadata

            @returns number of nodes added
        """
        last_updated = database_timestamp_to_datetime(news_website[CONTENT_SOURCE_LAST_UPDATE])
        logger.log(MY_INFO_LEVEL, "Last updated news_website is "+str(last_updated))
        #news_type_node = get_type_metanode(self.graph_db, CONTENT_TYPE_MODEL_NAME)

        # We need this node to add HAS_INSTANCE_RELATION
        nodes_to_add = []
        newest, newest_id = database_timestamp_to_datetime(0), 0 # Find newest news in the set
        for id, news in enumerate(list_of_news):
            d_news = pubdate_to_datetime(news["pubdate"])

            if d_news > last_updated:

                nodes_to_add.append(news)  # assume is dictionary
                if d_news > newest:
                    newest = d_news
                    newest_id = id

        if len(nodes_to_add) == 0:
            logger.log(MY_INFO_LEVEL, "Warning: No nodes added for "+str(news_website[CONTENT_SOURCE_LINK]))
            return 0

        logger.log(MY_INFO_IMPORTANT_LEVEL, "Updating last_updated to "+str(newest))

        self.odm_client.set(news_website["uuid"],
            {
                CONTENT_SOURCE_LAST_UPDATE: GMTdatetime_to_database_timestamp(newest)
            }
        )

        # Count exisiting nodes
        existing_nodes = len(self.odm_client.get_all_children\
                (parent_uuid=news_website["uuid"], rel_name="<<HAS_INSTANCE_RELATION>>",
                 title=nodes_to_add[newest_id]["title"]))



        if existing_nodes > 0:
            logger.log(MY_CRITICAL_LEVEL, "")
            logger.log(MY_CRITICAL_LEVEL, nodes_to_add[0])
            logger.log(MY_CRITICAL_LEVEL, existing_nodes)
            logger.log(MY_CRITICAL_LEVEL, "ERROR: Existing nodes ! Probably something wrong with "+unicode(news_website))
            return 0


        for n in nodes_to_add:
            n["uuid"] = self.odm_client.add_node(model_name=CONTENT_TYPE_MODEL_NAME, node_params=n)["uuid"]
            self.odm_client.add_rel(start_node_uuid=news_website["uuid"],
                                    end_node_uuid=n["uuid"],
                                    rel_type=PRODUCES_RELATION,
                                    rel_params={}
                                    )


        logger.log(MY_INFO_LEVEL, "Updating NewsWebsite "+unicode(news_website))
        logger.log(MY_INFO_LEVEL, "Added for instance "+unicode(nodes_to_add[0]["title"]))
        return len(nodes_to_add)


    def _fetch_news(self, news_website, newer_than=None):
        """
            @param newer_than date after which stop fetching.
                Note : due to timezone awareness might be not working.
            @param news_website is a dictionary (with uri)
            @returns lists of all news of website
        """
        if news_website[CONTENT_SOURCE_RSS_TYPE] != "rss":
            raise NotImplementedError()

        rss_link = news_website[CONTENT_SOURCE_LINK]

        try:
            response = urllib2.urlopen(rss_link)
            html = response.read()
            doc = xml.dom.minidom.parseString(html)
            feed = doc.childNodes[0].getElementsByTagName("channel")[0].getElementsByTagName("item")
            #<root>-><rss>-><channel>
        except Exception, e:
            logger.log(MY_CRITICAL_LEVEL, "Warning: Incorrect RSS format ")
            logger.log(MY_CRITICAL_LEVEL, "Warning: " + str(e))
            return []

        # Default iteration stop
        if newer_than is None:
            logger.log(MY_INFO_LEVEL, ("News website "+news_website[CONTENT_SOURCE_LINK],
                "last_updated ", database_timestamp_to_datetime(news_website[CONTENT_SOURCE_LAST_UPDATE]))
            )
            newer_than = database_timestamp_to_datetime(news_website[CONTENT_SOURCE_LAST_UPDATE])

        logger.log(MY_INFO_LEVEL, "Fetching news from "+str(rss_link)+" newer_than "+str(newer_than))


        def try_get_node_value(node, value, default = u""):
            """ Note we return everything as unicode !! """
            try:
                childNodes = node.getElementsByTagName(value)[0].childNodes
                for child in childNodes:
                    text = child.nodeValue
                    text = text.strip()
                    if text != "": return text
                return ""
            except:
                return default

        news_nodes = []

        for id,item in enumerate(feed):
            news_node = {}
            news_node["title"] = unicode(try_get_node_value(item, "title"))
            news_node["guid"] = unicode(try_get_node_value(item, "guid"))
            news_node["description"] = unicode(try_get_node_value(item, "description"))
            news_node["link"] = unicode(try_get_node_value(item, "link"))
            news_node["loved_counter"] = 0

            d = pubdate_to_datetime(try_get_node_value(item, "pubDate"))

            news_node[CONTENT_PUBDATE_TIMESTAMP] = GMTdatetime_to_database_timestamp(d)

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





