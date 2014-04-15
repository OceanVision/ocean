graph_workers
=============

This directory contains *Graph Workers* implementations
and `graph_workers` Python package with modules used in them.

spidercrab_master.py
--------------------

See wiki or use `-h` option for details

spidercrab_slave.py
-------------------

See wiki or use `-h` option for details

graph_worker_manager.py
-----------------------

(deprecated)

Use this script to start workers (it manages for example news_fetcher).

web_crawler_export.py
-----------------------

Use this script to instant crawl from any website.

Example:

    ./web_crawler_export.py https://news.google.com

It will start from `https://news.google.com` and crawl from there. The results
will be saved as python dictionaries in (as default) `rss_feeds` file.

You can use this file with `scripts/ocean_exemplary_data.py` script to import
data into database.

### Some useful facts and tricks:

1. You can run and terminate this script repeatedly and every time its output
will be **APPENDED** to the same file.

2. ... unless you change to another file by editing the script.

3. You can run this script number of times **SIMULTANEOUSLY**. That means you
can speed up a progress of crawling and append output to the same file at the
same time.

4. After doing 3. , when your `rss_feeds` file is ready, you must throw away
doubled data from file:

    `sort rss_feeds | uniq >> consistent_rss_feeds`

