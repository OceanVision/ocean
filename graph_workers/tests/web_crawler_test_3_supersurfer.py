"""
web_crawler_test_2_supersurfer
The name of this test means that crawler will jump often to the distant
locations, increasing his depth quickly.
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
    max_external_expansion = 4,
    max_crawling_depth = 64,
)

master_crawler.run()

time.sleep(60*60*24*3)
master_crawler.terminate()

