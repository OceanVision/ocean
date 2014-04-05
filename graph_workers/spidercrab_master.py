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
        default=Spidercrab.CONFIG_FILE_NAME,
        help='Use other config file than default spidercrab.json.\n'
             'NOTE: If there is no such a file, Spidercrab will create'
             'it for you there, based on spidercrab.json.default.'
    )
    (options, args) = parser.parse_args()

    # Spidercrab master launch is simple as hell
    spidercrab_master = Spidercrab.create_master(
        config_file_name=options.config_file_name
    )
    spidercrab_master.run()