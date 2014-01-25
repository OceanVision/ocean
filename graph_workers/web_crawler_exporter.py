doc = """
This script starts crawling from a given website and exports channels data.
"""

__author__ = 'Konrad Talik <konradtalik@gmail.com>'

import sys
import time

sys.path.append('web_crawler')
from web_crawler import WebCrawler

sys.path.append('.')
from privileges import construct_full_privilege, privileges_bigger_or_equal

EXPORT_FILE = 'rss_feeds'

if len(sys.argv) == 1:
    print doc
    print 'Usage: python2 web_crawler_exporter.py [WEBSITE]'
    print 'where [WEBSITE] is a full url, for example: http://news.google.com'
    print 'See README.md for details.'

print 'Output will be APPENDED to file named ' + EXPORT_FILE + '\n'

if len(sys.argv) == 1:
    exit()

master_crawler = WebCrawler.create_master (
    privileges = construct_full_privilege(),
    start_url = str(sys.argv[1]),
)

WebCrawler.create_worker (
    privileges = construct_full_privilege(),
    master = master_crawler,
    max_external_expansion = 1000,
    max_internal_expansion = 4,
    max_crawling_depth = 3,
    list_export = True,
    export_dicts = True,
    export_file = EXPORT_FILE,
)

master_crawler.run()

while master_crawler.is_working():
    time.sleep(1)

master_crawler.terminate()
time.sleep(2)

