#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
    Exemplary data for neo4j database
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


if __name__ == '__main__':

    print 'Running', __file__
    print 'This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*'
    print 'NOTE: This script *already executes* ocean_init_graph.py.'
    print 'Press enter to proceed...'
    enter = raw_input()

    os.system('./ocean_init_graph.py')

    # Create connection
    graph_db = neo4j.GraphDatabaseService(
        'http://{0}:{1}/db/data/'.format(
            get_configuration("neo4j", "host"),
            get_configuration("neo4j", "port")
        )
    )

    read_batch = neo4j.ReadBatch(graph_db)
    write_batch = neo4j.WriteBatch(graph_db)

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
    query = """
        MATCH (m:Model {model_name: '%s'}), (w:%s)
        CREATE (m)-[:`%s`]->(w)
        RETURN m,w
    """
    query %= (
        WEBSITE_TYPE_MODEL_NAME,
        WEBSITE_TYPE_MODEL_NAME,
        HAS_INSTANCE_RELATION,
    )
    write_batch.append_cypher(query)
    write_batch.submit()

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
    query = """
        MATCH (m:Model {model_name: '%s'}), (w:%s)
        CREATE (m)-[:`%s`]->(w)
        RETURN m,w
    """
    query %= (
        CONTENT_SOURCE_TYPE_MODEL_NAME,
        CONTENT_SOURCE_TYPE_MODEL_NAME,
        HAS_INSTANCE_RELATION,
    )
    write_batch.append_cypher(query)
    write_batch.submit()

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

