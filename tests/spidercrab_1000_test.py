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
    time.sleep(1)
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
            \\"news_fetch_max\\": 25,
            \\"terminate_when_fetched\\": 1
        }
        """,
        TEMP_SPIDERCRAB_CONFIG
    )
    print command
    os.system(command)
    print 'Contents:'
    os.system('cat ' + TEMP_SPIDERCRAB_CONFIG)

    master_thread = threading.Thread(target=run_master)
    master_thread.start()

    print '\nRunning 10 slaves...'
    command = '../graph_workers/spidercrab_slave.py -o -n 10 -c %s -t %s'
    command %= (TEMP_SPIDERCRAB_CONFIG, TEMP_SPIDERCRAB_STATS_EXPORT)
    print command
    time.sleep(1)
    os.system(command)

    print '\nStats:'
    os.system('cat ' + TEMP_SPIDERCRAB_STATS_EXPORT)

    stats = json.load(open(TEMP_SPIDERCRAB_STATS_EXPORT))
    print stats

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