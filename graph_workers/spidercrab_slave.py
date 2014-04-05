#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    spidercrab_slave.py - run Spidercrab slave worker with configuration
    located in your spidercrab.json (or whatever). Note that configuration
    can be partially overwritten (merged) with parameters given from master.
"""

from optparse import OptionParser
from threading import Thread

from spidercrab import Spidercrab

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '-c',
        '--config',
        dest='config_file_name',
        default=Spidercrab.CONFIG_FILE_NAME,
        help='Use other config file than default spidercrab.json.\n'
             'NOTE: If there is no such a file, Spidercrab will create'
             'it for you there, based on spidercrab.json.default.\n'
             'NOTE: Remember that configuration can be partially overwritten'
             ' (merged) with parameters given from master (read wiki for '
             'more information).'
    )
    parser.add_option(
        '-n',
        '--number',
        dest='number',
        default=1,
        help='Number of slaves to launch',
        type='int'
    )
    (options, args) = parser.parse_args()

    # Simplicity at its best
    for i in range(options.number):
        worker = Spidercrab.create_worker(
            config_file_name=options.config_file_name,
            runtime_id=str(i)
        )
        thread = Thread(target=worker.run)
        thread.start()