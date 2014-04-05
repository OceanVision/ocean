#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Exemplary data *from JSON* for neo4j database
    NOTE: wipes database !
    Connection done using RESTApi and wrapper for python py2neo
"""

import time
import sys
import uuid
import os

from py2neo import neo4j
from py2neo import node, rel

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))

from don_utils import get_configuration

sys.path.append('../graph_workers/')
lib_path = os.path.abspath('./graph_workers')
sys.path.append(lib_path)
from graph_workers.graph_defines import *
from odm_client import ODMClient

SOURCE_FILE = 'data/content_sources'

# TODO: Po co?
def get_node_value(node, value):
    searched_nodes = node.getElementsByTagName(value)
    if searched_nodes:
        childs = searched_nodes[0].childNodes
        if childs:
            return childs[0].nodeValue.strip()
    return ""


if __name__ == '__main__':

    print 'Running', __file__
    print 'With this script ContentSource nodes dicts from', SOURCE_FILE,\
        'file will be added.'
    print 'This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*'
    print 'NOTE: See README.md for details before running this script.'
    print '\nPlease turn *OFF* the odm_server (Lionfish).'
    print 'Press Enter to continue or Ctrl+C to abort.'
    enter = raw_input()

    os.system('./ocean_init_graph.py')

    # Create connection
    graph_db = neo4j.GraphDatabaseService(
        'http://{0}:{1}/db/data/'.format(
            get_configuration('neo4j', 'host'),
            get_configuration('neo4j', 'port')
        )
    )

    print '\nPlease turn *ON* the ODM now and press Enter.'
    print '(You are permitted to run whole system too during this process)'
    enter = raw_input()

    odm_client = ODMClient()
    odm_client.connect()

    # Read file contents
    content_sources_list = []

    print 'Reading source file', SOURCE_FILE, '...'

    try:
        f = open(SOURCE_FILE, 'r')
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
        print 'Add', str(i)+'/'+str(len(content_sources_list)), cs[:-1], '...'
        # TODO: Gather metadata with web_crawler and read from file
        try:
            cs_node = eval(cs)
            cs_node['last_updated'] = 0

            content_source_response = odm_client.create_node(
                CONTENT_SOURCE_TYPE_MODEL_NAME,
                HAS_INSTANCE_RELATION,
                **cs_node
            )

        except Exception as e:
            print '... Error occurred with adding `', cs[:-1], '`:'
            print e
            print 'Continuing...\n'

    odm_client.disconnect()

    print 'Graph populated successfully. GOODBYE AND GOOD LUCK!'

