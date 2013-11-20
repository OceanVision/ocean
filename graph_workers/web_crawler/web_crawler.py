"""
Web-crawling graph worker

    Web crawler is able to:

    - crawl, that is:

        1. Receive a content from a given http url.
        2. Parse a content to get a new urls list.
        3. Enqueue new urls to crawling.

    - start crawling from specified website
    - update database with new content (RSS feeds urls)
"""

import sys
import threading
import random
import urllib2
import urlparse
from HTMLParser import HTMLParser
import socket
import httplib
import multiprocessing
import time
import re

from py2neo import neo4j
from py2neo import node, rel

sys.path.append("..")
from graph_worker import GraphWorker
from utils import *
from privileges import construct_full_privilege, privileges_bigger_or_equal
# import defines for fields
from graph_defines import *
#from utils import logger

# Workaround replacement class for logger from utils package
#TODO: Find out how to mute logger from within another modules
#      (f.e. mute py2neo from WebCrawler class)
class LoggerReplacement():


    def date(self):
        string = unicode(time.localtime()[0]) + '-'
        string += unicode(time.localtime()[1]) + '-'
        string += unicode(time.localtime()[2]) + ' ' + unicode(time.time())
        return string


    def info(self, string):
        print "[I]", self.date(), '\t', string


logger = LoggerReplacement()


class WebCrawlerHTMLParser(HTMLParser):
    """
        WebCrawlerHTMLParser parses only one html content
        and saves useful data in collections.

        Example:

            wcparser = WebCrawlerHTMLParser()
            # Prepare work (needed after actions with another content)
            wcparser.clean(http_url)
            # Provide a content to parsing
            wcparser.feed(html_content)
            # Access parsed data
            for href in wcparser.found_internal_hrefs:
                print href

    """

    # Links belonging to this current domain
    found_internal_hrefs = []
    # Links to pages from another domains
    found_external_hrefs = []
    # Links to another domains
    found_domains_hrefs = []
    # Links to rss feeds of this site
    found_rss_feeds = []

    domain_url = ''

    def handle_starttag(self, tag, attrs):
        is_rss = False
        is_http = False

        for attr in attrs:

            if attr[0] == "type" and attr[1] == "application/rss+xml":
                is_rss = True
            if attr[0] == "href" and (
                    urlparse.urlsplit( attr[1] )[0] == "http" or
                    urlparse.urlsplit( attr[1] )[0] == "https"
            ):
                is_http = True
                http_url = attr[1]

        # Collect explicit RSS feeds
        if is_rss and is_http:
            self.found_rss_feeds.append( unify_url(http_url) )

    def clear(self, current_url):
        """
            Use this method to prepare to work a new set of data
        """
        self.found_internal_hrefs = []
        self.found_external_hrefs = []
        self.found_domains_hrefs = []
        self.found_rss_feeds = []
        self.domain_url = get_domain_url( current_url )


class WebCrawlerJob(object):
    """
        Object used to define job in job list for WebCrawlers
    """
    url = ""
    from_url = ""
    distance = 0
    #node_id = None

    def __init__(self, url, from_url, distance):
        self.url = url
        self.from_url = from_url
        self.distance = distance
        #self.node_id = node_id


class WebCrawlerJobList(object):
    """
        Object used to collect WebCrawlerJobs for WebCrawlers
    """
    manager = multiprocessing.Manager()
    job_list = manager.list()

    def __init__(self, job_list=None):
        if job_list:
            self.job_list = job_list

    def enqueue(self, job):
        self.job_list.insert(0, job)

    def pop(self):
        return self.job_list.pop()

    def __len__(self):
        return len(self.job_list)


class WebCrawler(GraphWorker):
    """
        Web crawling worker
    """
    required_privileges = construct_full_privilege()
    terminate_event = multiprocessing.Event()
    parser = WebCrawlerHTMLParser()


    @staticmethod
    def create_master(**params):
        if len(params) > 2:
            raise Exception("Wrong param list")

        return WebCrawler(**params)


    @staticmethod
    def create_worker(master, **params):
        if len(params) < 1:
            raise Exception("Wrong param list")
        params["master"] = master
        wc = WebCrawler(**params)
        master.workers.append(wc)
        return wc


    def __init__ (
        self,
        privileges,
        start_url=None,
        master=None,
        neo4j_url="http://localhost:7474/db/data/",
        max_internal_expansion=50,              # max number of pages of every website to explore
        max_external_expansion=50,              # max number of external links to check from every website
        max_rss_expansion=float('inf'),         # max number of rss feeds to extract from every website
        max_crawling_depth=2,                   # max (external) distance from start_url
        max_database_updates=500,               # max number of rss feeds to insert into a database
        verbose=False
    ):
        """
            Construct WebCrawler.
            Every max_* argument can be set to float('inf') which means none limitations.
        """

        self.max_internal_expansion = max_internal_expansion
        self.max_external_expansion = max_external_expansion
        self.max_rss_expansion = max_rss_expansion
        self.max_crawling_depth = max_crawling_depth
        self.max_database_updates = max_database_updates
        self.verbose = verbose

        if not privileges_bigger_or_equal(privileges, self.required_privileges):
            raise Exception("Not enough privileges")

        self.graph_db = neo4j.GraphDatabaseService(neo4j_url)

        if master == None:
            self.level = "master"
            self.workers = []
            self.master = self
            # Init first job
            if start_url == None:
                start_url = self._get_random_newsfeed()[NEWS_WEBSITE_LINK]
                logger.info("No start_url provided - selected " + str(start_url) + " !")
            start_url_node_id = self._get_url_db_node_id(start_url)
            self.job_list = WebCrawlerJobList()
            self.job_list.enqueue( WebCrawlerJob ( start_url, None, 0 ) )
        else:
            self.level = "worker"
            self.master = master


    def terminate(self):
        if self.level == "master":
            for worker in self.workers:
                worker.terminate()
        self.terminate_event.set()


    def get_required_privileges(self):
        return required_privileges


    def has_job(self, job):
        for j in self.job_list.job_list:
            if j.url == job.url:
                return True
        return False


    def add_job(self, job):
        self.job_list.enqueue(job)


    def jobs(self):
        return len(self.job_list)


    def run(self):
        """
            Start crawling.
        """

        # Tasks for master level web_crawler
        if self.level == "master":
            pro = []

            for worker in self.workers:
                pro.insert ( 0, multiprocessing.Process(target = worker.run) )

            for process in pro:
                process.start()

            return

        elif self.level != "worker":
            pass

        # Here self.level == "worker"
        self.visited = [] #TODO: Database solution
        self.db_updates_counter = 0

        while not self.terminate_event.is_set():

            # No job = sleep ^__^
            if self.master.jobs() == 0:
                logger.info ("No jobs... Waiting...")
                time.sleep(4)
                while self.master.jobs() == 0:
                    time.sleep(5)
                continue

            # Take job
            my_job = self.master.job_list.pop()
            if self._visited(my_job.url):
                print "Already visited", my_job.url
                continue

            logger.info ("Jobs: " + str(self.master.jobs()+1) )
            logger.info (
                ". Entering (depth: "
                + str(my_job.distance) + ") "
                + my_job.url + " ..."
            )

            # While exploring the website we have a "local" jobs to do
            # We start from a page given by master job
            website_jobs = WebCrawlerJobList (
                [ 
                    WebCrawlerJob ( my_job.url, None, my_job.distance )
                ]
            )
            # This list exist to prevent redundancy in internal hrefs
            considered_hrefs = [ my_job.url ]

            # Here we collect ALL finds from the whole website
            found_hrefs = []
            # using lsts of hrefs divided by destination type
            found_internal_hrefs = []
            found_external_hrefs = []
            found_domains_hrefs = []
            found_rss_feeds = []

            # Here we collect only limited lists of hrefs (with limitations)
            external_hrefs = []
            domains_hrefs = []
            rss_feeds = []

            # 1. Explore all pages of this website (with the limitations)
            internal_visits = 0
            while (
                len(website_jobs) > 0
                and internal_visits < self.max_internal_expansion
            ):
                # Pop next url
                website_job = website_jobs.pop()
                current_url = website_job.url
                if self._visited(current_url):
                    continue

                if self.verbose:
                    logger.info ( "... Parsing:")
                    logger.info ( unicode(website_job.from_url)
                        + " -> " + unicode(current_url)
                    )
                # 1.1. Receive page content from a given http url.
                html = get_html(current_url)
                if not html:
                    continue

                internal_visits += 1
                self.visited.append(current_url) #TODO: Database solution

                # 1.2. Parse the content to get a new urls list.

                # Parse explicit rss feeds
                self.parser.clear(current_url)
                self.parser.feed(html)

                # Find ANY existing urls
                found_hrefs = find_urls(html)

                # 1.3. Clean up founded data

                # Divide hrefs to internal, external and domains
                current_url_domain = get_domain_url(current_url)
                for href in found_hrefs:
                    # Reject unwanted urls
                    if not valid_url(href):
                        continue
                    href_domain = get_domain_url(href)
                    # Check if it is the same domain
                    if href_domain == current_url_domain:
                        if self.verbose:
                            logger.info ( "Int. href: " + unicode(href) )
                        found_internal_hrefs.append ( unify_url(href) )
                    else:
                        if self.verbose:
                            logger.info ( "Ext. href: " + unicode(href) )
                        found_external_hrefs.append ( unify_url( href ) )
                        found_domains_hrefs.append ( get_domain_url( href ) )

                # Collect rss_feeds
                for href in self.parser.found_rss_feeds:
                    if len(rss_feeds) < self.max_rss_expansion:
                        if not href in rss_feeds:
                            logger.info("Found new feed! - " + href + " :)")
                            rss_feeds.append(href)
                    else:
                        break

                # Collect internal_hrefs
                for href in found_internal_hrefs:
                    if len(website_jobs) < self.max_internal_expansion:
                        if not href in considered_hrefs:
                            website_jobs.enqueue (
                                WebCrawlerJob (
                                    href, current_url, my_job.distance
                                )
                            )
                            considered_hrefs.append(href)
                    else:
                        break

                # Collect domains_hrefs
                for href in found_domains_hrefs:
                    if len(domains_hrefs) < self.max_external_expansion:
                        if not href in domains_hrefs:
                            domains_hrefs.insert(0,href)
                    else:
                        break

            # End of website pages exploration (1.)

            # 2. Update database with new rss feeds
            logger.info("Updating database...")
            for feed in rss_feeds:
                if self.db_updates_counter < self.max_database_updates:
                    if not self._visited(feed):
                        if self._update_feed(feed):
                            self.db_updates_counter += 1
                else:
                    self.terminate_event.set()
                    break

            # 3. Enqueue new jobs
            if my_job.distance < self.max_crawling_depth:
                for href in domains_hrefs:
                    if valid_url(href):
                        job = WebCrawlerJob (
                            href, my_job.url, my_job.distance+1
                        )
                        #if not self.master.has_job(job):
                        self.master.add_job(job)

            logger.info (
                "Found:\t" + str(len(considered_hrefs)) + " int. urls,\t"
                + str(len(domains_hrefs)) + " ext. urls,\t"
                + str(len(rss_feeds)) + " rsses.\n"
            )

        # End of run
        logger.info( str(self) + " done.")


    def _visited(self, site_url):
        """
            @returns if site with given url has been visited
        """
        #TODO: Database query
        return site_url in self.visited


    def _get_url_db_node_id(self, site_url):
        """
            @returns db node id of given url
        """
        site_node = self._get_url_db_node(site_url)
        if site_node:
            return site_node._id
        else:
            return None


    def _get_url_db_node(self, site_url):
        """
            @returns db node (only one!) object of given url
        """
        result = self._get_url_db_nodes(site_url)
        if result[0]:
            return result[0]
        else:
            return None


    def _update_feed(self, feed_url):
        """
           Updates graph database with new feeds.
        """

        feed_url = feed_url.encode("utf8")
        root = self.graph_db.node(0)
        #rels = list(self.graph_db.match(start_node=root, rel_type=HAS_TYPE_RELATION))
        #print self.graph_db.relationship(rels[0]._id)
        if not self._get_url_db_node(feed_url):
            read_batch = neo4j.ReadBatch(self.graph_db)
            # Find NewsWebsite type nodes root
            read_batch.append_cypher (
                u'''
                start n=node(0)
                match (n)-[r:`'''
                + unicode(HAS_TYPE_RELATION)
                + u'''`]->(m)
                where m.name = "rss:NewsWebsite" return m;
                '''
            )
            result = read_batch.submit()
            news_websites_root = result[0]
            write_batch = neo4j.WriteBatch(self.graph_db)
            # Create new node
            node_properties = node (
                title = "New RSS Feed",
                description = "None",
                link = feed_url,
                source_type = "rss",
                label = NEWS_WEBSITE_LABEL,
                last_updated = int(time.time()),
                language = "Unknown"
            )
            rss_node, = self.graph_db.create(node_properties)
            logger.info( rss_node )
            # Create relationship
            self.graph_db.create (
                rel(news_websites_root, HAS_INSTANCE_RELATION, rss_node)
            )
            return True
        return False



    def _get_url_db_nodes(self, site_url):
        """
            @returns db node(s) object list of given url
                     (there may be more than one)
        """

        site_url = site_url.encode("utf8")
        read_batch = neo4j.ReadBatch(self.graph_db)
        read_batch.append_cypher (
            u'''
            start n = node(*)
            where HAS(n.label) and n.label = "__news_website__" and n.link = \"''' +
            unicode (site_url) + u'''\"
            return n;
            '''
        ) #TODO: Better search
        result = read_batch.submit()
        return result


    def _get_random_newsfeed(self):
        #TODO: Think about moving this method to GraphWorker class
        # and improve _get_all_newsfeeds() or use another method.
        """
            @returns random news feed from database as py2neo.node
        """
        all_feeds = self._get_all_newsfeeds()
        selection = random.randint( 0, len(all_feeds)-1 )
        return all_feeds[selection]


    def _get_all_newsfeeds(self):
        """
            @returns lists of all news feeds in the system (as py2neo.node,
                note: you can refer to properties by node["property"] and
                to id by node._id :)
        """

        read_batch = neo4j.ReadBatch(self.graph_db)
        read_batch.append_cypher( # will return list of records :)
            """
            start n=node(*)
            where HAS(n.label) and n.label = "__news_website__"
            return n;
            """
        ) #TODO: inefficient.
        news_websites = []
        logger.info("Submiting query!")
        result = read_batch.submit()
        for record in result[0]:
            news_websites.append(record.n)
        return news_websites

