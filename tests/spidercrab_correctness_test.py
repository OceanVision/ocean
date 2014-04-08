#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Test correctness of the Spidercrab.
    WARNING: Wipes database!
    NOTE: Test should take about 4 minutes.
"""

import os
import time


if __name__ == '__main__':

    TEMP_URL_LIST_FILE = '../data/spidercrab_correctness_test_urls'
    TEMP_SPIDERCRAB_CONFIG = '../data/spidercrab_correctness_test_config'
    TEMP_SLAVES_EXPORT_FILE = '../data/spidercrab_correctness_test_export'

    files = [
        TEMP_URL_LIST_FILE,
        TEMP_SPIDERCRAB_CONFIG,
        TEMP_SLAVES_EXPORT_FILE
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

    print '\nWiping neo4j...'
    os.system('../scripts/ocean_init_graph.py')

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
            \\"worker_id\\": \\"spidercrab_correctness_test_worker\\"
        }
        """,
        TEMP_SPIDERCRAB_CONFIG
    )
    print command
    os.system(command)
    print 'Contents:'
    os.system('cat ' + TEMP_SPIDERCRAB_CONFIG)

    # TODO: Automatize below action
    print '\nPlease *(RE)START* the Lionfish ODM now and press Enter...'
    enter = raw_input()

    print '\nRunning Spidercrab master with option to enqueue above sources.'
    command = '../graph_workers/spidercrab_master.py -s %s -c %s'
    command %= (TEMP_URL_LIST_FILE, TEMP_SPIDERCRAB_CONFIG)
    print command
    time.sleep(1)
    os.system(command)

    print '\nRunning 10 slaves (One ContentSource for every slave)...'
    command = '../graph_workers/spidercrab_slaves.py -n 10 -c %s -e %s'
    command %= (TEMP_SPIDERCRAB_CONFIG, TEMP_SLAVES_EXPORT_FILE)
    print command
    time.sleep(1)
    os.system(command)

    print '\nFinished! spidercrab_slaves.py export file contents:'
    os.system('cat ' + TEMP_SLAVES_EXPORT_FILE)

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