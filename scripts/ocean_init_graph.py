#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    This script initializes graph with default data, needed to start working
    with a database and/or Lionfish (creates meta-nodes).
    NOTE: Creates root node (0) if not present :)
"""

import sys
import os
import uuid


from py2neo import neo4j
from py2neo import node, rel

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))

from don_utils import get_configuration

sys.path.append('../graph_workers/')
from graph_defines import *

APP_LABEL = 'rss'



def run_and_return_type_list():
    # Create connection        
    neo4j_port = None
    neo4j_host = None
    graph_db = neo4j.GraphDatabaseService(
            'http://{0}:{1}/db/data/'.format(neo4j_host if neo4j_host else
        get_configuration("neo4j","host"), neo4j_port if  neo4j_port else get_configuration("neo4j", "port"))
        )
    # graph_db = neo4j.GraphDatabaseService('http://localhost:7474/db/data/')

    print 'Running', __file__
    print 'This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*'
    print 'NOTE: The Root node is required to exist in database.'
    print 'Press enter to proceed...'
    enter = raw_input()

    read_batch = neo4j.ReadBatch(graph_db)
    read_batch.append_cypher('MATCH n RETURN count(n)')
    print 'Nodes in graph initially ', read_batch.submit()
    print 'Erasing nodes and relations'
    read_batch.clear()

    # Erases database data without the Root node
    write_batch = neo4j.WriteBatch(graph_db)
    write_batch.append_cypher('MATCH ()-[r]-() DELETE r')
    write_batch.append_cypher('MATCH n DELETE n')
    write_batch.submit()
    write_batch.clear()

    # Sanity check
    read_batch.append_cypher('MATCH (n) RETURN count(n)')
    result = read_batch.submit()
    print 'Nodes in graph erased. Sanity check : ', result
    read_batch.clear()

    if result[0] > 0:
        raise Exception('Not erased graph properly')

    # Configures the Root node
    write_batch.append_cypher('CREATE (n:Root {uuid: "root"}) RETURN id(n)')
    root_result = write_batch.submit()
    write_batch.clear()

    root = graph_db.node(root_result[0])
    root.add_labels('Node')

    # ===================== MODELS =====================
    type_list = [
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+NEOUSER_TYPE_MODEL_NAME,
            model_name=NEOUSER_TYPE_MODEL_NAME
        ),
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+TAG_TYPE_MODEL_NAME,
            model_name=TAG_TYPE_MODEL_NAME
        ),
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+CONTENT_SOURCE_TYPE_MODEL_NAME,
            model_name=CONTENT_SOURCE_TYPE_MODEL_NAME
        ),
        node(
            uuid=str(uuid.uuid1()),
            app_label=APP_LABEL,
            name=APP_LABEL+':'+CONTENT_TYPE_MODEL_NAME,
            model_name=CONTENT_TYPE_MODEL_NAME
        )
    ]

    type_list = graph_db.create(*type_list)
    for item in type_list:
        item.add_labels('Model', 'Node')

    # Creates type relations
    graph_db.create(
        rel(root, HAS_TYPE_RELATION, type_list[0]),
        rel(root, HAS_TYPE_RELATION, type_list[1]),
        rel(root, HAS_TYPE_RELATION, type_list[2]),
        rel(root, HAS_TYPE_RELATION, type_list[3])
    )

    print 'Graph populated successfully.'

    return type_list


if __name__ == "__main__":
    run_and_return_type_list()
