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

APP_LABEL = 'rss'

if __name__ == '__main__':
    # Create connection
    graph_db = neo4j.GraphDatabaseService('http://{0}:{1}/db/data/'.format(get_configuration("neo4j","host"), get_configuration("neo4j","port")))
    # graph_db = neo4j.GraphDatabaseService('http://localhost:7474/db/data/')

    print 'This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*\
, press enter to proceed'
    enter = raw_input()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher('match (n) return count(n);')
    print 'Nodes in graph initially ', my_batch.submit()
    print 'Erasing nodes and relations'

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher('match (a)-[r]-(b) delete r;')
    # fix: do not delete the root
    my_batch.append_cypher('match (n) WHERE ID(n) <> 0 delete n ;')
    my_batch.submit()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher('match (n) return count(n);')
    result = my_batch.submit()
    print 'Nodes in graph erased. Sanity check : ', result
    """
    if result[0] != 1:
        raise Exception('Not erased graph properly')
        exit(1)
    """

    root = graph_db.node(0)

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
            uuid='973eb80a-a07d-11e3-9f3a-2cd05ae1c39b',
            app_label=APP_LABEL,
            name=APP_LABEL+':'+NEWS_WEBSITE_TYPE_MODEL_NAME,
            model_name=NEWS_WEBSITE_TYPE_MODEL_NAME
        ),
    ]
    old_types = graph_db.create(*old_types)
    for item in old_types:
        item.add_labels('Node', 'Model')

    # Create old version type relations
    graph_db.create(
        rel(root, HAS_TYPE_RELATION, old_types[0])
    )
    #NOTE: End of future deletion

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

    # 1.9 doesnt support labels!
    #map(lambda u: u.add_labels(USER_LABEL),users) # Add labels
    #print [x for x in  graph_db.find(USER_LABEL)] # Sanity check,

    ### Add websites ###
    websites = [
        node(
            uuid='97678546-a07d-11e3-9f3a-2cd05ae1c39b',
            link='http://www.gry-online.pl/',
            title='GRY-OnLine',
            language='pl',
        ),
        node(
            uuid='976787bc-a07d-11e3-9f3a-2cd05ae1c39b',
            link='http://www.wp.pl/',
            title='Wirtualna Polska',
            language='pl',
        ),
        node(
            uuid='97678938-a07d-11e3-9f3a-2cd05ae1c39b',
            link='http://www.tvn24.pl/',
            title='TVN24.pl - Wiadomosci z kraju i ze swiata',
            language='pl',
        ),
    ]
    websites = graph_db.create(*websites)
    for item in websites:
        item.add_labels('Node', 'Website')

    # Create instance relations
    graph_db.create(
         rel(types[0], HAS_INSTANCE_RELATION, websites[0]),
         rel(types[0], HAS_INSTANCE_RELATION, websites[1]),
         rel(types[0], HAS_INSTANCE_RELATION, websites[2])
    )

    # Create nodes
    content_sources_list = [
        node(
            uuid='977466da-a07d-11e3-9f3a-2cd05ae1c39b',
            link='http://www.gry-online.pl/rss/news.xml',
            title='GRY-OnLine Wiadomosci',
            description='Najnowsze Wiadomosci',
            image_width='144',
            image_height='18',
            image_link='http://www.gry-online.pl/S012.asp',
            image_url='http://www.gry-online.pl/rss/rss_logo.gif',
            language='pl',
            last_updated=int(time.time() - 100000),
            source_type='rss'
        ),
        node(
            uuid='97746a22-a07d-11e3-9f3a-2cd05ae1c39b',
            link='http://wiadomosci.wp.pl/kat,1329,ver,rss,rss.xml',
            title='Wiadomosci WP - Wiadomosci - Wirtualna Polska',
            description='Wiadomosci.wp.pl to serwis, dzieki ktoremu mozna \
zapoznac sie z biezaca sytuacja w kraju i na swiecie.',
            image_width='70',
            image_height='28',
            image_link='http://wiadomosci.wp.pl',
            image_url='http://i.wp.pl/a/i/finanse/logozr/WP.gif',
            language='pl',
            last_updated=int(time.time() - 1000000),
            source_type='rss'
        ),
        node(
            uuid='97746bf8-a07d-11e3-9f3a-2cd05ae1c39b',
            link='http://www.tvn24.pl/najwazniejsze.xml',
            title='TVN24.pl - Wiadomosci z kraju i ze swiata - najnowsze \
informacje w TVN24',
            description='Czytaj najnowsze informacje i ogladaj wideo w portalu \
informacyjnym TVN24! U nas zawsze aktualne wiadomosci z kraju, ze swiata, \
relacje na zywo i wiele wiecej.',
            language='pl',
            last_updated=int(time.time() - 100000),
            source_type='rss'
        )
    ]

    # Create content sources
    content_sources = graph_db.create(*content_sources_list)
    for item in content_sources:
        item.add_labels('Node', 'ContentSource')

    # Create ContentSources instance relations
    graph_db.create(
        rel(types[3], HAS_INSTANCE_RELATION, content_sources[0]),
        rel(types[3], HAS_INSTANCE_RELATION, content_sources[1]),
        rel(types[3], HAS_INSTANCE_RELATION, content_sources[2])
    )

    # Create Website __has__ ContentSource relations
    graph_db.create(
        rel(websites[0], HAS_RELATION, content_sources[0]),
        rel(websites[1], HAS_RELATION, content_sources[1]),
        rel(websites[2], HAS_RELATION, content_sources[2])
    )

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher('create index on :Node(uuid)')
    my_batch.append_cypher('create index on :ContentSource(link)')
    my_batch.submit()

    ##TODO: Delete following code after system refactorization
    ## Create old type websites
    #old_websites = graph_db.create(*content_sources_list)
    #
    ## Create old type websites instance relations
    #graph_db.create(
    #    rel(old_types[0], HAS_INSTANCE_RELATION, old_websites[0]),
    #    rel(old_types[0], HAS_INSTANCE_RELATION, old_websites[1]),
    #    rel(old_types[0], HAS_INSTANCE_RELATION, old_websites[2])
    #)
    ##NOTE: End of future deletion
    #
    ##map(lambda w: w.add_labels(NEWS_CHANNELS_LABEL),channels) # Add labels
    ##print [x for x in  graph_db.find(NEWS_CHANNELS_LABEL)] # Sanity check
    #
    #
    #graph_db.create(
    #    rel(users[0], SUBSCRIBES_TO_RELATION, content_sources[2]),
    #    rel(users[0], SUBSCRIBES_TO_RELATION, content_sources[1]),
    #    rel(users[1], SUBSCRIBES_TO_RELATION, content_sources[1]),
    #)
#        rel(users[2], SUBSCRIBES_TO_RELATION, content_sources[0]),
#        rel(users[3], SUBSCRIBES_TO_RELATION, content_sources[0]),
#    )

    # Adding news is working, so we do not need to populate graph with news
    #news = [
    #node(
    #    label=NEWS_LABEL, link='http://konflikty.wp.pl/kat,106090,title,Nowe-smiglowce-USA-Wielki-projekt-'
    #                           'zbrojeniowy-w-cieniu-budzetowych-ciec,wid,16116470,wiadomosc.html?ticaid=111908',
    #    title='Wypadek busa w Egipcie. Rannych zostalo dwoch Polakow',
    #    description='Szesciu cudzoziemcow, w tym dwoch Polakow, zostalo rannych w wypadku drogowym w Egipcie. '
    #                'Do zdarzenia doszlo na drodze miedzy Kairem a Aleksandria - informuje serwis ruvr.ru.',
    #    guuid='http://wiadomosci.wp.pl/kat,1329,title,Wypadek-busa-w-Egipcie-Rannych-zostalo-dwoch-Polakow,wid,'
    #         '16151839,wiadomosc.html'
    #)
    #, node(
    #    label=NEWS_LABEL, link='http://www.tvn24.pl/naukowcy-slady-polonu-w-ciele-arafata-sugeruja-udzial-osob-'
    #                           'trzecich,369594,s.html',
    #    title='Naukowcy: slady polonu w ciele Arafata sugeruja udzial osob trzecich',
    #    description='Palestynskiego lidera otruto w roku 2004.',
    #    guuid='http://www.tvn24.pl/naukowcy-slady-polonu-w-ciele-arafata-sugeruja-udzial-osob-trzecich,369594,s.html'
    #)
    #]
    #
    #news = graph_db.create(*news)  # Create nodes in graph database
    ##map(lambda w: w.add_labels(NEWS_LABEL),news) # Add labels
    #
    #graph_db.create(
    #rel(users[0], SUBSCRIBES_TO_RELATION, websites[2]),
    #rel(users[0], SUBSCRIBES_TO_RELATION, websites[1]),
    #rel(users[1], SUBSCRIBES_TO_RELATION, websites[1]),
    #rel(websites[1], PRODUDES_RELATION, news[0]),
    #rel(websites[2], PRODUDES_RELATION, news[1])
    #)
    #
    #graph_db.create(
    #rel(types[2], HAS_INSTANCE_RELATION, news[0]),
    #rel(types[2], HAS_INSTANCE_RELATION, news[1])
    #)

    print 'Graph populated successfully'

