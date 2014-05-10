#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Specific of the Spidercrab on 1000 nodes.
    WARNING: Wipes database!
"""

import json
import os
import threading
import time


def run_master():
    print '\nRunning two masters with option to enqueue above sources.'
    cmd = '../graph_workers/spidercrab_master.py -o -n 2 -c %s -t %s'
    cmd %= (TEMP_SPIDERCRAB_CONFIG, TEMP_SPIDERCRAB_STATS_EXPORT)
    print cmd
    os.system(cmd)


def run_slave():
    print '\nRunning 10 slaves...'
    cmd = '../graph_workers/spidercrab_slave.py -o -n 10 -c %s -t %s'
    cmd %= (TEMP_SPIDERCRAB_CONFIG, TEMP_SPIDERCRAB_STATS_EXPORT)
    print cmd
    time.sleep(1)
    os.system(cmd)


if __name__ == '__main__':

    DATA_FILE = '../data/contentsource_nodes_1000'

    TEMP_SPIDERCRAB_CONFIG = '../data/spidercrab_1000_test_config'
    TEMP_SPIDERCRAB_STATS_EXPORT = \
        '../data/spidercrab_1000_test_stats'
    files = [
        TEMP_SPIDERCRAB_CONFIG,
        TEMP_SPIDERCRAB_STATS_EXPORT,
    ]

    NUMBER_OF_SLAVES = 10
    NEWS_TO_BE_FETCHED = 25  # for each slave

    print 'Running', __file__
    print '\nNOTE: You need following file to run this test ' \
        '(Ocean Don Corleone Server):'
    print DATA_FILE

    # Security stuff
    error = False
    for temp_file in files:
        if os.path.isfile(temp_file):
            error = True
            print 'WARNING: file', temp_file, 'already exists!'
            print 'Remove it or change the path inside this script!'
    if error:
        exit(1)

    os.chdir('../scripts/')

    print '\nWiping and filling database with 1000 nodes...'
    command = '../scripts/ocean_exemplary_data.py -s %s'
    command %= DATA_FILE
    os.system(command)

    os.chdir('../tests/')

    print '\nCreating Spidercrab config file...'
    command = 'echo "%s" > %s'
    command %= (
        """
        {
            \\"update_interval_s\\": 10,
            \\"graph_worker_id\\": \\"1000_test_spidercrab\\",
            \\"sources_enqueue_portion\\": 25,
            \\"terminate_on_end\\": 1,
            \\"news_fetch_max\\": %s,
            \\"terminate_when_fetched\\": 1
        }
        """,
        TEMP_SPIDERCRAB_CONFIG
    )
    command %= NEWS_TO_BE_FETCHED
    print command
    os.system(command)
    print 'Contents:'
    os.system('cat ' + TEMP_SPIDERCRAB_CONFIG)

    master_thread = threading.Thread(target=run_master)
    master_thread.start()
    time.sleep(1)

    print '\nRunning 10 slaves...'
    command = '../graph_workers/spidercrab_slave.py -o -n %s -c %s -t %s'
    command %= (
        NUMBER_OF_SLAVES,
        TEMP_SPIDERCRAB_CONFIG,
        TEMP_SPIDERCRAB_STATS_EXPORT
    )
    print command
    time.sleep(1)
    os.system(command)

    print '\nStats:'
    os.system('cat ' + TEMP_SPIDERCRAB_STATS_EXPORT)

    stats = json.load(open(TEMP_SPIDERCRAB_STATS_EXPORT))
    print '\n', stats

    print '\nChecking results...'
    slaves = stats['1000_test_spidercrab']['slave']
    for slave in slaves:
        if_passed = 'NOT PASSED :('
        if slave['stats']['total_fetched_news'] >= NEWS_TO_BE_FETCHED:
            if_passed = 'PASSED :)'
        print 'Slave ' + str(slave['runtime_id']) + ' fetched '\
            + str(slave['stats']['total_fetched_news'])\
            + '/' + str(NEWS_TO_BE_FETCHED) + ' news...' + if_passed


    print '\nResult files created under following paths:'
    for temp_file in files:
        print temp_file
    print 'Please copy/rename them if you want keep them.'
    print 'If not - press Enter.'
    enter = raw_input()

    # Security stuff
    for temp_file in files:
        print 'Removing', temp_file
        if not os.path.isfile(temp_file):
            print '... no such a file or file.'
        else:
            os.remove(temp_file)