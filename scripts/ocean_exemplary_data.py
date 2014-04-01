#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Exemplary data for neo4j database
Note : wipes database !
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

APP_LABEL = 'rss'
SOURCE_FILE = 'data/rss_feeds'


def get_node_value(node, value):
    searched_nodes = node.getElementsByTagName(value)
    if searched_nodes:
        childs = searched_nodes[0].childNodes
        if childs:
            return childs[0].nodeValue.strip()
    return ""



if __name__ == "__main__":
    # Create connection
    graph_db = neo4j.GraphDatabaseService("http://{0}:{1}/db/data/".format(get_configuration("neo4j","host"), get_configuration("neo4j","port"))

    print 'With this script rss urls from', SOURCE_FILE, 'file will be added.'
    print 'NOTE: See README.md for details before running this script!!!'
    print 'WARINING: This script will *ERASE ALL NODES AND RELATIONS IN NEO4J\
DATABASE*'
    print '\nPlease turn *OFF* the ODM. Press Enter to proceed, Ctrl+C to abort.'
    enter = raw_input()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher("START n=node(*) return count(n);")
    print "Nodes in graph initially ", my_batch.submit()
    print "Erasing nodes and relations"

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher("start r=relationship(*) delete r;")
    # fix: do not delete the root
    my_batch.append_cypher("start n=node(*) WHERE ID(n) <> 0 delete n ;")
    my_batch.submit()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher("START n=node(*) return count(n);")
    result = my_batch.submit()
    print "Nodes in graph erased. Sanity check : ", result

    if result[0] != 1:
        raise Exception("Not erased graph properly")
        exit(1)

    root = graph_db.node(0)

    ### Add webservice types ###
    types = [
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+WEBSITE_TYPE_MODEL_NAME,
            model_name=WEBSITE_TYPE_MODEL_NAME
        ),
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+NEOUSER_TYPE_MODEL_NAME,
            model_name=NEOUSER_TYPE_MODEL_NAME
        ),
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+CONTENT_TYPE_MODEL_NAME,
            model_name=CONTENT_TYPE_MODEL_NAME
        ),
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+CONTENT_SOURCE_TYPE_MODEL_NAME,
            model_name=CONTENT_SOURCE_TYPE_MODEL_NAME
        )
    ]
    types = graph_db.create(*types)

    # Create type relations
    graph_db.create(
        rel(root, HAS_TYPE_RELATION, types[0]),
        rel(root, HAS_TYPE_RELATION, types[1]),
        rel(root, HAS_TYPE_RELATION, types[2]),
        rel(root, HAS_TYPE_RELATION, types[3])
    )

    #TODO: Delete following code after system refactorization
    # Old version types
    old_types = [
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+NEWS_WEBSITE_TYPE_MODEL_NAME,
            model_name=NEWS_WEBSITE_TYPE_MODEL_NAME
        ),
    ]
    old_types = graph_db.create(*old_types)

    # Create old version type relations
    graph_db.create(
        rel(root, HAS_TYPE_RELATION, old_types[0])
    )
    #NOTE: End of future deletion

    ### Add users ###
    # Create nodes
    users = [
        node(uuid=str(uuid.uuid1()), username="kudkudak"),
        node(uuid=str(uuid.uuid1()), username="konrad"),
        node(uuid=str(uuid.uuid1()), username="brunokam"),
        node(uuid=str(uuid.uuid1()), username="szymon")
    ]
    users = graph_db.create(*users)
    # Create instance relations
    graph_db.create(
        rel(types[1], HAS_INSTANCE_RELATION, users[0]),
        rel(types[1], HAS_INSTANCE_RELATION, users[1]),
        rel(types[1], HAS_INSTANCE_RELATION, users[2]),
        rel(types[1], HAS_INSTANCE_RELATION, users[3])
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
            cs_node['last_updated'] = int(time.time() - 100000)

            content_source_response = odm_client.add_node(
                CONTENT_SOURCE_TYPE_MODEL_NAME,
                cs_node,
            )

            ### Create Website __has__ ContentSource relations ###

            '''website_response = odm_client.add_node(
                WEBSITE_TYPE_MODEL_NAME,
                {
                    'link': cs_node['link'],
                    'title': cs_node['title'],
                    'language': cs_node['language'],
                }
            )'''

            # TODO: Gather and read data that will contain actual metadata
            '''odm_client.add_rel(
                website_response['uuid'],
                content_source_response['uuid'],
                HAS_RELATION
            )'''

        except Exception as e:
            print '... Error occurred with `', cs[:-1], '`:'
            print e
            print 'Continuing...\n'

    odm_client.disconnect()

    print 'Graph populated successfully. GOODBYE AND GOOD LUCK!'

