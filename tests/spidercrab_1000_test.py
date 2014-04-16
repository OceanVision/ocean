#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Specific of the Spidercrab on 1000 nodes.
    WARNING: Wipes database!
"""

import os
import time


if __name__ == '__main__':

    DATA_FILE = '../data/contentsource_nodes_1000'

    TEMP_SPIDERCRAB_CONFIG = '../data/spidercrab_1000_test_config'

    files = [
        TEMP_SPIDERCRAB_CONFIG
    ]

    print 'Running', __file__
    print 'NOTE: You need following file to run this test ' \
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
    command = 'python2 ocean_exemplary_data.py -s %s'
    command %= DATA_FILE
    os.system(command)

    os.chdir('../tests/')

    print '\nCreating Spidercrab config file...'
    command = 'echo "%s" > %s'
    command %= (
        """
        {
            \\"update_interval_s\\": 600,
            \\"graph_worker_id\\": \\"1000_test_spidercrab\\",
            \\"terminate_on_end\\": 1
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
    command = '../graph_workers/spidercrab_master.py -c %s'
    command %= TEMP_SPIDERCRAB_CONFIG
    print command
    time.sleep(1)
    os.system(command)

    print '\nRunning 10 slaves...'
    command = '../graph_workers/spidercrab_slave.py -n 10 -c %s'
    command %= TEMP_SPIDERCRAB_CONFIG
    print command
    time.sleep(1)
    os.system(command)

    print '\nFinished!'

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