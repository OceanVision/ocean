#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Exemplary data *from JSON* for neo4j database
    NOTE: wipes database !
    Connection done using RESTApi and wrapper for python py2neo
"""

import sys
import os
from optparse import OptionParser

from py2neo import neo4j

sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../lionfish/python_lionfish/client/'))
from don_utils import get_configuration

sys.path.append('../graph_workers/')
from graph_defines import *
from client import Client

SOURCE_FILE = '../data/contentsource_nodes_exemplary'


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option(
        '-s',
        '--contentsource-nodes-file',
        dest='contentsource_nodes_file',
        default=SOURCE_FILE,
        help='Input file, where every line is a ContentSource node '
             '(in a dictionary form). You can generate this file with '
             'spidercrab_slave.py, webcrawler_export.py, write it yourself '
             'or get it from Ocean Don Corleone server. More info on wiki. '
             '(Default: ' + SOURCE_FILE + ')'
    )
    (options, args) = parser.parse_args()

    print 'Running', __file__
    print 'With this script ContentSource nodes dicts from', SOURCE_FILE,\
        'file will be added.'
    print 'This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*'
    print 'NOTE: See README.md for details before running this script.'
    print 'Press Enter to continue or Ctrl+C to abort.'
    enter = raw_input()

    retcode = os.system('python2 ocean_init_graph.py')

    if retcode != 0:
        print "FAILED ocean_init_graph.py. Exiting"
        exit(1)

    # Create connection
    graph_db = neo4j.GraphDatabaseService(
        'http://{0}:{1}/db/data/'.format(
            get_configuration('neo4j', 'host'),
            get_configuration('neo4j', 'port')
        )
    )

    odm_client = Client('localhost', 7777)
    odm_client.connect()
    odm_batch = odm_client.get_batch()

    # Read file contents
    content_sources_list = []

    print 'Reading source file', options.contentsource_nodes_file, '...'

    try:
        f = open(options.contentsource_nodes_file, 'r')
        try:
            content_sources_list = f.readlines()
        finally:
            f.close()
    except IOError as e:
        print e
        exit()

    print 'Populating database...'

    # Create nodes
    i = 0
    for cs in content_sources_list:
        i += 1
        print 'Adding ' + str(i) + '/' + str(len(content_sources_list)) +\
            ' ' + str(cs[:-1]) + ' to batch...'
        try:
            cs_node = eval(unicode(cs))
            cs_node['last_updated'] = 0
            cs_node['description'] = cs_node['description'].encode('utf-8')

            odm_batch.append(
                odm_client.create_node,
                CONTENT_SOURCE_TYPE_MODEL_NAME,
                HAS_INSTANCE_RELATION,
                **cs_node
            )
            if i % 25 == 0 or i == len(content_sources_list)-1:
                print 'Submitting batch... Please have patience...'
                odm_batch.submit()
        except Exception as e:
            print '... Error occurred with adding `', cs[:-1], '`:'
            print e
            print 'Continuing...\n'

    odm_client.disconnect()

    print 'Graph populated successfully. GOOD NIGHT AND GOOD LUCK!'
