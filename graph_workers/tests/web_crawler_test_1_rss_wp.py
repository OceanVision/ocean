"""
web_crawler_test_1_rss_wp.py
This simple test fetches 10 RSS feeds from rss.wp.pl website and then quits.
"""

import sys
import time

sys.path.append("../web_crawler")
from web_crawler import WebCrawler

sys.path.append("..")
from privileges import construct_full_privilege, privileges_bigger_or_equal


master_crawler = WebCrawler.create_master (
    privileges = construct_full_privilege(),
    start_url = "http://rss.wp.pl/"
)


WebCrawler.create_worker (
    master = master_crawler,
    privileges = construct_full_privilege(),
    max_internal_expansion = 10,
    max_database_updates = 10
)

master_crawler.run()

time.sleep(120)
master_crawler.terminate()

