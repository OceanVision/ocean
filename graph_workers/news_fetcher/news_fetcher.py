"""
Prototype for job fetching news.

First version support threads and workers very locally (cannot scale beyond single machine).append

News fetcher definition - Graph Worker working on sources of content, which are rss feeds :)
Currently it measns working on all NewsWebsites


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

NewsFetcherJob = namedtuple("NewsFetcherJob", 'url worktime')
"""
    url - url of news website to pull news from
    worktime - when to pull news
"""

graph_db = None # Work on one graph_db connection for now

class NewsFetcher(GraphWorker):
    required_privileges = construct_full_privilege()
    minimum_time_delta_to_update = 0 #TODO: replace

    def __init__(self, privileges, master_descriptor=None):
        if not privileges_bigger_or_equal(privileges, NewsFetcher.required_privileges):
            raise Exception("Not enough privileges")
        self.privileges = copy.deepcopy(privileges)
        if master_descriptor is None:
            self.type = "master"
            # Very prototypical implementation of worker/master : note in the future there is ONE global job list :)
            self.global_job_list = [] # We can assume that this is "almost sorted" time-wisely
        else:
            self.type = "worker"
            self.master_descriptor = master_descriptor
        pass


    def get_required_privileges(self):
        return NewsFetcher.required_privileges

    @staticmethod
    def create_master(**params):
        if len(params) != 1:
            raise Exception("Wrong param list")

        return NewsFetcher(**params)

    @staticmethod
    def create_worker(master_descriptor, **params):
        if len(params) != 1:
            raise Exception("Wrong param list")
        params["master_descriptor"] = master_descriptor
        return NewsFetcher(**params)


    def run(self):
        pass









def test_1():
    """ Basic test for news_fetcher """
    nf_master = NewsFetcher.create_master(privileges=construct_full_privilege())
    nf_worker = NewsFetcher.create_worker(nf_master, privileges=construct_full_privilege())
    nf_master.run()
    nf_worker.run()


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


def get_all_newsfeeds(graph_db):
    """
        @returns lists of all news feeds in the system (as py2neo.node,
            note: you can refer to properties by node["property"] and
            to id by node._id :)
    """
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher( # will return list of records :)
        """
        start n=node(*)
        where id(n)<>0 and HAS(n.label) and n.label = "__news_website__"
        return n;
        """
    ) #TODO: inefficient.
    news_websites = []
    result = my_batch.submit()
    for record in result[0]:
        news_websites.append(record.n)
    return news_websites


#TODO: note, that this is quite slow : this is why scala is needed
def fetch_news(news_website, newer_than=None):
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

    def try_get_node_value(node, value, default = u""):
        """ Note we return everything in unicode !! """
        try:
            return unicode(node.getElementsByTagName(value)[0].firstChild.nodeValue)
        except:
            return default


    news_nodes = []
    for id,item in enumerate(feed):
        news_node = {}
        news_node["title"] = try_get_node_value(item, "title")
        news_node["guid"] = try_get_node_value(item, "guid")
        news_node["description"] = try_get_node_value(item, "description")
        news_node["link"] = try_get_node_value(item, "link")


        d = pubdate_to_datetime(try_get_node_value(item, "pubDate"))
        if newer_than is not None:
            if (d - newer_than) < timedelta(second = 0): # check for sign
                break
        #print "Hello"
        #print d
        #print try_get_node_value(item, "pubDate")
        #print datetime_to_pubdate(d)
        news_node["pubdate"] = datetime_to_pubdate(d)
        news_nodes.append(news_node)

    return news_nodes

def add_news_to_graph(news_website, graph_db, list_of_news):
    """
        @param news_website -
            node to which we will attach the news
            **note** : assumes that are sorted newer to older !!!

        Adds news to graph taking care of all metadata
    """

    #TODO: "<" in queries is not accepted by Cypher
    last_updated = datetime.fromtimestamp(news_website[NEWS_WEBSITE_LAST_UPDATE])
    news_type_node = get_type_metanode(graph_db, NEWS_TYPE_MODEL_NAME) #TODO: it should be cached somewhere

    # We need this node to add HAS_INSTANCE_RELATION
    nodes_to_add = []
    for news in list_news:
        # !! I am assuming here GMT time !!
        # TODO: Convert everything to UTC?
        d_news = pubdate_to_datetime(news["pubdate"]).replace(tzinfo=None)
        if not (d_news>last_updated) > 0:
            break
        news["label"] = NEWS_LABEL # add metadata
        nodes_to_add.append(py2neo.node(**news)) # assume is dictionary


    if len(nodes_to_add) == 0:
        logger.warning("No nodes added")
        return

    last_updated_current = pubdate_to_datetime(nodes_to_add[0]["pubdate"])

    nodes_added = graph_db.create(*nodes_to_add)

    logger.info(nodes_added[0])

    instance_relations = [py2neo.rel(news_type_node, HAS_INSTANCE_RELATION, content)
                          for content in nodes_added]
    produces_relations = [py2neo.rel(news_website, PRODUDES_RELATION, content)
                          for content in nodes_added]

    logger.info(news_type_node)

    logger.info("Creating necessary metadata")
    graph_db.create(*instance_relations)
    logger.info("Created instance metadata relations")
    graph_db.create(*produces_relations)

    logger.info("Updating NewsWebsite "+str(news_website))
    news_website.update_properties(
        {
            NEWS_WEBSITE_LAST_UPDATE:
                int(time.mktime(last_updated_current.timetuple()))
        }
    ) # using graph_db used to fetch this node!!


    logger.info(news_type_node)


if __name__ == "__main__":
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    nf = get_all_newsfeeds(graph_db)
    for n in nf:
        list_news = fetch_news(n)
        add_news_to_graph(n, graph_db, list_news)
