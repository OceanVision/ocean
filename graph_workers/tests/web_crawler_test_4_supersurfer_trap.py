"""
web_crawler_test_4_supersurfer.py
This supersurfer is in a trap.
Expanding only 2 first exteral urls from each website (not random choice)
will lead to trap, becouse of repetition of most popular websites urls
like google.com, twitter.com, facebook.com etc.
"""

import sys
import time

sys.path.append("../web_crawler")
from web_crawler import WebCrawler

sys.path.append("..")
from privileges import construct_full_privilege, privileges_bigger_or_equal


master_crawler = WebCrawler.create_master (
    privileges = construct_full_privilege(),
    start_url = "http://antyweb.pl/"
)


WebCrawler.create_worker (
    privileges = construct_full_privilege(),
    master = master_crawler,
    max_internal_expansion = 5,
    max_external_expansion = 2,
    max_crawling_depth = 100,
)

master_crawler.run()

time.sleep(60*60*24*3)
master_crawler.terminate()

