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

from don_corleone import don_utils as du

spidercrabs = []
spidercrab_slave_threads = []


def are_spidercrab_slaves_running():
    for spidercrab_thread in spidercrabs:
        if spidercrab_thread.is_alive():
            return True
    return False


def get_spidercrab_graph_workers():
    """
        Useful method when importing this script.
    """
    if are_spidercrab_slaves_running():
        raise RuntimeWarning('Spidercrab slave is currently running!')
    else:
        return spidercrabs


if __name__ == '__main__':

    default_number = 1
    default_export_file_name = None
    default_export_stats_file_name = None

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
        '-t',
        '--export-stats-to',
        dest='export_stats_to',
        default=default_export_stats_file_name,
        help='Export stats of executed graph workers when they finish.'
             '\nNOTE: You can set this option in Don Corleone config under '
             'the "export_stats_to" key.'
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
        spidercrab_slave = Spidercrab.create_worker(
            config_file_name=options.config_file_name,
            runtime_id=str(i),
            export_stats_to=options.export_stats_to,
            export_cs_to=options.export_file_name,
            no_corleone=options.no_corleone,
        )
        thread = Thread(target=spidercrab_slave.run)
        thread.start()
        spidercrab_slave_threads.append(thread)
        spidercrabs.append(spidercrab_slave)