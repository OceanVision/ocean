#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    spidercrab_master.py - run Spidercrab master worker with configuration
    located in your spidercrab.json (or whatever)
"""

import os
import sys

from optparse import OptionParser
from spidercrab import Spidercrab

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))
from don_utils import get_configuration

if __name__ == '__main__':

    default_sources_url_file = ''

    try:
        default_number = get_configuration(
            'spidercrab_master', 'sources_urls_file')
    except Exception as error:
        print error

    parser = OptionParser()
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
    spidercrab_master = Spidercrab.create_master(
        config_file_name=options.config_file_name,
        master_sources_urls_file=options.sources_urls_file,
        no_corleone=options.no_corleone,
    )
    spidercrab_master.run()