#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    spidercrab_master.py - run Spidercrab master worker with configuration
    located in your spidercrab.json (or whatever)
"""

from optparse import OptionParser

from spidercrab import Spidercrab

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '-c',
        '--config',
        dest='config_file_name',
        default='',
        help='Use other config file than from Don Corleone.\n'
             'NOTE: If there is no such a file, Spidercrab will create'
             'it for you there, based on spidercrab.json.template. (It will '
             'also generate a config in Don Corleone if not present.)'
    )
    parser.add_option(
        '-s',
        '--sources-urls-file',
        dest='sources_file_name',
        default='',
        help='Path to file, where every line contains url address to new '
             'ContentSources that will be added to the database and '
             'flagged as pending to update (checks if url already exist in '
             'the database).'
    )
    (options, args) = parser.parse_args()

    # Spidercrab master launch is simple as hell
    spidercrab_master = Spidercrab.create_master(
        config_file_name=options.config_file_name,
        master_sources_urls_file=options.sources_file_name,
    )
    spidercrab_master.run()