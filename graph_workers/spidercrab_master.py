#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    spidercrab_master.py - run Spidercrab master worker with configuration
    located in your spidercrab.json (or whatever)
"""

import os
import sys

from optparse import OptionParser
from threading import Thread

from spidercrab import Spidercrab

from don_corleone import don_utils as du

spidercrabs = []
spidercrab_master_threads = []


def are_spidercrab_masters_running():
    for spidercrab_thread in spidercrab_master_threads:
        if spidercrab_thread.is_alive():
            return True
    return False


def get_spidercrab_graph_workers():
    """
        Useful method when importing this script.
    """
    if are_spidercrab_masters_running():
        raise RuntimeWarning('Spidercrab master is currently running!')
    else:
        return spidercrabs


if __name__ == '__main__':

    don_config = dict()
    try:
        don_config = don_config = du.get_running_service(
            service_name='spidercrab_master',
            node_id=du.get_my_node_id(),
            enforce_running=False
        )['service_config']
    except Exception as error:
        print str(error)

    default_number = don_config.get('number', 1)
    default_sources_url_file = don_config.get('sources_urls_file', '')
    default_export_stats_file_name = don_config.get('export_stats_to', None)

    parser = OptionParser()
    parser.add_option(
        '-n',
        '--number',
        dest='number',
        default=default_number,
        type='int',
        help='Number of threads to launch. \nNOTE: You can set this option '
             'in Don Corleone config under the "number" key.'
    )
    parser.add_option(
        '-c',
        '--config',
        dest='config_file_name',
        default='',
        help='Use other config file than from Don Corleone.\n'
             'NOTE: If there is no such a file, Spidercrab will create '
             'it for you there, based on spidercrab.json.template.'
    )
    parser.add_option(
        '-s',
        '--sources-urls-file',
        dest='sources_urls_file',
        default=default_sources_url_file,
        help='Path to file, where every line contains url address to new '
             'ContentSource that will be added to the database and '
             'flagged as pending to update (checks if url already exist in '
             'the database).\nNOTE: You can set this option in Don Corleone '
             'config under the "sources_urls_file" key.'
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

    # Spidercrab master launch is simple as hell
    for i in range(options.number):
        spidercrab_master = Spidercrab.create_master(
            config_file_name=options.config_file_name,
            runtime_id=str(i),
            export_stats_to=options.export_stats_to,
            master_sources_urls_file=options.sources_urls_file,
            no_corleone=options.no_corleone,
        )
        thread = Thread(target=spidercrab_master.run)
        thread.start()
        spidercrab_master_threads.append(thread)
        spidercrabs.append(spidercrab_master)