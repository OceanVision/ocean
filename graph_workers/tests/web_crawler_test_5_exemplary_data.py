"""
web_crawler_test_5_exemplary_data.py
This test starts from news.google.com in order to prepare exemplary data.
"""

import sys
import time

sys.path.append("../web_crawler")
from web_crawler import WebCrawler

sys.path.append("..")
from privileges import construct_full_privilege, privileges_bigger_or_equal


master_crawler = WebCrawler.create_master (
    privileges = construct_full_privilege(),
    start_url = "http://news.google.com/",
)


WebCrawler.create_worker (
    privileges = construct_full_privilege(),
    master = master_crawler,
    max_internal_expansion = 2,
    max_crawling_depth = 3,
    max_database_updates = 5000,
    list_export = True,
)

master_crawler.run()

time.sleep(60*60*24*3)
master_crawler.terminate()

