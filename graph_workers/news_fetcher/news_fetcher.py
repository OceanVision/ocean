"""
Prototype for job fetching news.

First version support threads and workers very locally (cannot scale beyond single machine).append


TODO: In the future communicate through postgresql/reimplement in Scala
"""
import sys
import copy
from collections import namedtuple
sys.path.append("..")
from graph_worker import GraphWorker
import logging
from privileges import construct_full_privilege, privileges_bigger_or_equal
from py2neo import neo4j
from py2neo import node, rel
from graph_defines import * # import defines for fields
from utils import logger
import urllib2
import xml.dom.minidom
from datetime import timedelta, datetime

NewsFetcherJob = namedtuple("NewsFetcherJob", 'url worktime')
"""
    url - url of news website to pull news from
    worktime - when to pull news
"""


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


def get_all_newsfeeds():
    """
        @returns lists of all news feeds in the system
    """
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher(
        """
        start n=node(*)
        where id(n)<>0 and HAS(n.label) and n.label = "__news_website__"
        return n;
        """
    ) #TODO: inefficient.
    news_websites = []
    result = my_batch.submit()
    for node in result[0]:
        properties = node.n.get_properties()
        properties["uri"] = node.n.__uri__
        news_websites.append((node, properties))
    return news_websites


#TODO: note, that this is quite slow : this is why scala is needed
def fetch_news(news_website, newer_than=None):
    """
        @param newer_than date after which stop fetching
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



    for id,item in enumerate(feed):
        news_node = {"title":""}
        try:
            news_node["title"] = item.getElementsByTagName("title")[0].firstChild.nodeValue
        except:
            logger.warning("Empty title")

        rss_time = item.getElementsByTagName("pubDate")[0].firstChild.nodeValue
        rss_time_tok = rss_time.replace(",","").replace(":"," ").split(" ")

        d = None
        # Different time formats. Propses .. omg
        try:
            d = datetime.strptime(rss_time, "%a, %d %b %Y %H:%M:%S %Z") if \
                len(rss_time_tok[3]) > 2 else time.strptime(rss_time, "%a, %d %b %y %H:%M:%S %Z")
        except:
            # PYTHON 2.7 DOESNT SUPPORT %z DIRECTIVE !!!.. omg, official documentation..
            try:
                offset = int(rss_time[-5:])
                delta = timedelta(hours=offset/100)
                d = datetime.strptime(rss_time[:-6], "%a, %d %b %Y %H:%M:%S") if \
                    len(rss_time_tok[3]) > 2 else datetime.strptime(rss_time[:-6], "%a, %d %b %y %H:%M:%S")
                d -= delta
            except Exception, e:
                print e
                raise Exception("Wrong date format")

        news_node["pubdate"] = d



if __name__ == "__main__":
    nf = get_all_newsfeeds()
    for n in nf:
        fetch_news(n[1])

