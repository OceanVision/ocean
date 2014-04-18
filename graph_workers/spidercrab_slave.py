#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    spidercrab_slave.py - run Spidercrab slave worker with configuration
    located in your spidercrab.json (or whatever). Note that configuration
    can be partially overwritten (merged) with parameters given from master.
"""

import os
import sys

from optparse import OptionParser
from threading import Thread

from spidercrab import Spidercrab

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))
from don_utils import get_configuration

if __name__ == '__main__':

    default_number = 1

    try:
        default_number = get_configuration('spidercrab_slave', 'number')
    except Exception as error:
        print error

    default_export_file_name = None

    try:
        default_export_file_name = get_configuration(
            'spidercrab_slave', 'export_cs_to')
    except Exception as error:
        print error

    parser = OptionParser()
    parser.add_option(
        '-n',
        '--number',
        dest='number',
        default=default_number,
        type='int',
        help='Number of slaves to launch. \nNOTE: You can set this option in '
             'Don Corleone config under the "number" key.'
    )
    parser.add_option(
        '-c',
        '--config',
        dest='config_file_name',
        default='',
        help='Use other config file than from Don Corleone.\n'
             'NOTE: If there is no such a file, Spidercrab will create '
             'it for you there, based on spidercrab.json.default.\n'
             'NOTE: Remember that configuration can be partially overwritten '
             '(merged) with parameters given from master (read wiki for '
             'more information).'
    )
    parser.add_option(
        '-e',
        '--export-cs-to',
        dest='export_file_name',
        default=default_export_file_name,
        help='Export ContentSource nodes properties dictionaries to a '
             'file, where every line is a property dictionary (File '
             'can be later used by ocean_exemplary_data.py)\n'
             'NOTE: Lines will be APPENDED, which is good for threading. Be '
             'careful not to append the same data to existing file. \nNOTE: '
             'You can set this option in Don Corleone config under the '
             '"export_cs_to" key.'
    )
    parser.add_option(
        '-o',
        '--no-corleone',
        dest='no_corleone',
        action='store_true',
        default=False,
        help='Tells this Spidercrab that there is no Corleone running (That '
             'means an "offline" mode on).\nNOTE: Remember to pass a '
             'separate config file with `-c` option!'
    )
    (options, args) = parser.parse_args()

    # Simplicity at its best
    for i in range(options.number):
        worker = Spidercrab.create_worker(
            config_file_name=options.config_file_name,
            runtime_id=str(i),
            export_cs_to=options.export_file_name,
            no_corleone=options.no_corleone,
        )
        thread = Thread(target=worker.run)
        thread.start()
