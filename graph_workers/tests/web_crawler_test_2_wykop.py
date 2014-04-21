"""
web_crawler_test_2_wykop.py
This test precisely explores www.wykop.pl in search for RSS feeds.
"""

import sys
import time

sys.path.append("../web_crawler")
from web_crawler import WebCrawler

sys.path.append("..")
from privileges import construct_full_privilege, privileges_bigger_or_equal


master_crawler = WebCrawler.create_master (
    privileges = construct_full_privilege(),
    start_url = "http://www.wykop.pl/"
)


WebCrawler.create_worker (
    privileges = construct_full_privilege(),
    master = master_crawler,
    max_crawling_depth = 3
)

master_crawler.run()

time.sleep(60*60*24*3)
master_crawler.terminate()

