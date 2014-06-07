#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Test correctness of the Spidercrab.
    WARNING: Wipes database!
    NOTE: Test should take about 4 minutes.
"""

import os
import time
import sys
sys.path.append(os.path.abspath(".."))
from don_corleone import don_utils as du

if __name__ == '__main__':

    OCEAN_ROOT = du.get_ocean_root_dir()

    TEMP_URL_LIST_FILE = '../data/spidercrab_correctness_test_urls'
    TEMP_SPIDERCRAB_CONFIG = '../data/spidercrab_correctness_test_config'
    TEMP_SLAVE_EXPORT_FILE = '../data/spidercrab_correctness_test_export'

    files = [
        TEMP_URL_LIST_FILE,
        TEMP_SPIDERCRAB_CONFIG,
        TEMP_SLAVE_EXPORT_FILE
    ]

    print 'Running', __file__

    # Security stuff
    error = False
    for temp_file in files:
        if os.path.isfile(temp_file):
            error = True
            print 'WARNING: file', temp_file, 'already exists!'
            print 'Remove it or change the path inside this script!'
    if error:
        exit(1)

    print '\nTesting spidercrab<->system integrity...'
    os.system(OCEAN_ROOT + '/tests/spidercrab_integrity_test.py')

    print '\nWiping neo4j...'
    os.system(OCEAN_ROOT + '/scripts/ocean_init_graph.py')

    print '\nCreating a file with a list of urls...'
    urls = [
        'http://www.guardian.co.uk/artanddesign/rss',
        'http://www.guardian.co.uk/books/rss',
        'http://www.guardian.co.uk/business/rss',
        'http://www.guardian.co.uk/commentisfree/rss',
        'http://www.guardian.co.uk/sport/cricket/rss',
        'http://www.guardian.co.uk/education/rss',
        'http://www.guardian.co.uk/football/rss',
        'http://www.guardian.co.uk/sport/formulaone/rss',
        'http://feeds.guardian.co.uk/theguardian/rss',
        'http://feeds.guardian.co.uk/theguardian/technology/gamesblog/rss'
    ]
    for url in urls:
        command = 'echo "%s" >> %s'
        command %= (url, TEMP_URL_LIST_FILE)
        os.system(command)

    print 'Contents:'
    os.system('cat ' + TEMP_URL_LIST_FILE)

    print '\nCreating Spidercrab config file...'
    command = 'echo "%s" > %s'
    command %= (
        """
        {
            \\"update_interval_s\\": 600,
            \\"graph_worker_id\\": \\"spidercrab_correctness_test_worker\\",
            \\"terminate_on_end\\": 1
        }
        """,
        TEMP_SPIDERCRAB_CONFIG
    )
    print command
    os.system(command)
    print 'Contents:'
    os.system('cat ' + TEMP_SPIDERCRAB_CONFIG)
    time.sleep(1)

    print '\nRunning Spidercrab master with option to enqueue above sources.'
    command = OCEAN_ROOT + '/graph_workers/spidercrab_master.py -o -s %s -c %s'
    command %= (TEMP_URL_LIST_FILE, TEMP_SPIDERCRAB_CONFIG)
    print command
    time.sleep(1)
    os.system(command)

    print '\nRunning 10 slaves (One ContentSource for every slave)...'
    command = OCEAN_ROOT \
        + '/graph_workers/spidercrab_slave.py -o -n 10 -c %s -t %s'
    command %= (TEMP_SPIDERCRAB_CONFIG, TEMP_SLAVE_EXPORT_FILE)
    print command
    time.sleep(1)
    os.system(command)

    print '\nFinished! spidercrab_slave.py statistics export file contents:'
    os.system('cat ' + TEMP_SLAVE_EXPORT_FILE)

    print '\nResult files created under following paths:'
    for temp_file in files:
        print temp_file
    print 'Please copy/rename them if you want keep them.'
    print 'If not - press Enter.'
    enter = raw_input()

    # Security stuff
    for temp_file in files:
        print 'Removing', temp_file
        os.remove(temp_file)
