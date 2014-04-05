#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    This script initializes graph with default data, needed to start working
    with a database and/or Lionfish (creates meta-nodes).
    NOTE: Creates root node (0) if not present :)
"""

import sys
import os

from py2neo import neo4j
from py2neo import node, rel

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))

from don_utils import get_configuration

sys.path.append('../graph_workers/')
lib_path = os.path.abspath('./graph_workers')
sys.path.append(lib_path)
from graph_workers.graph_defines import *

APP_LABEL = 'rss'

if __name__ == '__main__':
    # Create connection
    graph_db = neo4j.GraphDatabaseService(
        'http://{0}:{1}/db/data/'.format(
            get_configuration("neo4j", "host"),
            get_configuration("neo4j", "port"))
    )

    print 'Running', __file__
    print 'This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*'
    print 'Press enter to proceed...'

    enter = raw_input()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher('match (n) return count(n);')
    nodes_count = my_batch.submit()
    print 'Nodes in graph initially', nodes_count
    print 'Erasing nodes and relations'

    if nodes_count == [0]:
        # Create root
        graph_db.create(node())

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher('match (a)-[r]-(b) delete r;')
    # fix: do not delete the root
    my_batch.append_cypher('match (n) where id(n) <> 0 delete n ;')
    my_batch.submit()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher('match (n) return count(n);')
    result = my_batch.submit()
    print 'Nodes in graph erased. Sanity check : ', result

    if result[0] != 1:
        raise Exception('Not erased graph properly')

    # Clear root
    my_batch.append_cypher(
        'MATCH (r) WHERE id(r) = 0 SET r = {};'
    )
    my_batch.submit()

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher('match (e:Root) set e.root=1;')
    my_batch.submit()

    ### Add webservice types ###
    types = [
        node(
            uuid='970f37f6-a07d-11e3-9f3a-2cd05ae1c39b',
            app_label=APP_LABEL,
            name=APP_LABEL+':'+WEBSITE_TYPE_MODEL_NAME,
            model_name=WEBSITE_TYPE_MODEL_NAME
        ),
        node(
            uuid='970f6d5c-a07d-11e3-9f3a-2cd05ae1c39b',
            app_label=APP_LABEL,
            name=APP_LABEL+':'+NEOUSER_TYPE_MODEL_NAME,
            model_name=NEOUSER_TYPE_MODEL_NAME
        ),
        node(
            uuid='970f9b7e-a07d-11e3-9f3a-2cd05ae1c39b',
            app_label=APP_LABEL,
            name=APP_LABEL+':'+CONTENT_TYPE_MODEL_NAME,
            model_name=CONTENT_TYPE_MODEL_NAME
        ),
        node(
            uuid='970fc9d2-a07d-11e3-9f3a-2cd05ae1c39b',
            app_label=APP_LABEL,
            name=APP_LABEL+':'+CONTENT_SOURCE_TYPE_MODEL_NAME,
            model_name=CONTENT_SOURCE_TYPE_MODEL_NAME
        )
    ]

    types = graph_db.create(*types)
    for item in types:
        item.add_labels('Node', 'Model')

    # Create type relations
    write_batch = neo4j.WriteBatch(graph_db)

    # Create instance relations
    query = """
            MATCH (r), (m:Model) WHERE id(r) = 0
            CREATE (r)-[:`%s`]->(m)
            RETURN r, m
        """
    query %= HAS_TYPE_RELATION
    write_batch.append_cypher(query)
    write_batch.submit()

    ### Add users ###
    # Create nodes
    users = [
        node(uuid='974ee6b2-a07d-11e3-9f3a-2cd05ae1c39b', username='kudkudak'),
        node(uuid='974ee946-a07d-11e3-9f3a-2cd05ae1c39b', username='konrad'),
        node(uuid='974eeacc-a07d-11e3-9f3a-2cd05ae1c39b', username='brunokam'),
        node(uuid='974eec34-a07d-11e3-9f3a-2cd05ae1c39b', username='szymon')
    ]
    users = graph_db.create(*users)
    for item in users:
        item.add_labels('Node', 'NeoUser')

    # Create instance relations
    graph_db.create(
        rel(types[1], HAS_INSTANCE_RELATION, users[0]),
        rel(types[1], HAS_INSTANCE_RELATION, users[1]),
        rel(types[1], HAS_INSTANCE_RELATION, users[2]),
        rel(types[1], HAS_INSTANCE_RELATION, users[3])
    )

    print 'Graph populated successfully'

