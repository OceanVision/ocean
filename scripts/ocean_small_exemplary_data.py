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

from py2neo import neo4j, node, rel

sys.path.append(os.path.join(os.path.dirname(__file__), '../don_corleone/'))

from don_utils import get_configuration

sys.path.append('../graph_workers/')
lib_path = os.path.abspath('./graph_workers')
sys.path.append(lib_path)
from graph_workers.graph_defines import *

APP_LABEL = 'rss'

if __name__ == '__main__':
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

    # ===================== USERS =====================
    # Creates nodes
    user_list = [
        node(uuid=str(uuid.uuid1()), username='kudkudak'),
        node(uuid=str(uuid.uuid1()), username='konrad'),
        node(uuid=str(uuid.uuid1()), username='brunokam'),
        node(uuid=str(uuid.uuid1()), username='szymon')
    ]

    user_list = graph_db.create(*user_list)
    for item in user_list:
        item.add_labels(NEOUSER_TYPE_MODEL_NAME, 'Node')

    # Creates instance relations
    graph_db.create(
        rel(type_list[0], HAS_INSTANCE_RELATION, user_list[0]),
        rel(type_list[0], HAS_INSTANCE_RELATION, user_list[1]),
        rel(type_list[0], HAS_INSTANCE_RELATION, user_list[2]),
        rel(type_list[0], HAS_INSTANCE_RELATION, user_list[3])
    )

    # ===================== TAGS =====================
    # Creates nodes
    tag_list = [
        node(uuid=str(uuid.uuid1()), tag='AssassinsCreedIV'),
        node(uuid=str(uuid.uuid1()), tag='FarCry3'),
        node(uuid=str(uuid.uuid1()), tag='Ubisoft'),
        node(uuid=str(uuid.uuid1()), tag='wynikisprzedazy'),
        node(uuid=str(uuid.uuid1()), tag='AssassinsCreed'),

        node(uuid=str(uuid.uuid1()), tag='FarCry'),
        node(uuid=str(uuid.uuid1()), tag='Krakow'),
        node(uuid=str(uuid.uuid1()), tag='Wisla'),
        node(uuid=str(uuid.uuid1()), tag='alarmpowodziowy'),
        node(uuid=str(uuid.uuid1()), tag='falawezbraniowa'),

        node(uuid=str(uuid.uuid1()), tag='IMGW'),
        node(uuid=str(uuid.uuid1()), tag='powodz'),
        node(uuid=str(uuid.uuid1()), tag='Lodz'),
        node(uuid=str(uuid.uuid1()), tag='deszcz'),
        node(uuid=str(uuid.uuid1()), tag='sygnalizacjaswietlna'),

        node(uuid=str(uuid.uuid1()), tag='RydzaSmiglego'),
        node(uuid=str(uuid.uuid1()), tag='Pilsudskiego'),
        node(uuid=str(uuid.uuid1()), tag='Bombaj'),
        node(uuid=str(uuid.uuid1()), tag='pogotowieprzeciwpowodziowe'),
        node(uuid=str(uuid.uuid1()), tag='Majchrowski'),

        node(uuid=str(uuid.uuid1()), tag='podtopienie'),
    ]

    tag_list = graph_db.create(*tag_list)
    for item in tag_list:
        item.add_labels(TAG_TYPE_MODEL_NAME, 'Node')

    # Creates instance relations
    for tag in tag_list:
        graph_db.create(rel(type_list[1], HAS_INSTANCE_RELATION, tag))

    # ===================== FEEDS =====================
    # Create nodes
    feed_list = [
        node(uuid=str(uuid.uuid1()), name='Moje miasto'),
    ]

    feed_list = graph_db.create(*feed_list)
    for item in feed_list:
        item.add_labels(FEED_TYPE_NAME, 'Node')

    # Creates instance relations
    graph_db.create(
        rel(user_list[2], HAS_FEED_RELATION, feed_list[0])
    )

    # Creates tag relations
    graph_db.create(
        rel(feed_list[0], HAS_INCLUDES_RELATION, tag_list[6])
    )
    graph_db.create(
        rel(feed_list[0], HAS_EXCLUDES_RELATION, tag_list[12])
    )

    # ===================== CONTENT SOURCES =====================
    # Creates nodes
    content_source_list = [
        node(
            uuid=str(uuid.uuid1()),
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
            uuid=str(uuid.uuid1()),
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
            uuid=str(uuid.uuid1()),
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

    content_source_list = graph_db.create(*content_source_list)
    for item in content_source_list:
        item.add_labels(CONTENT_SOURCE_TYPE_MODEL_NAME, 'Node')

    # Creates instance relations
    graph_db.create(
        rel(type_list[2], HAS_INSTANCE_RELATION, content_source_list[0]),
        rel(type_list[2], HAS_INSTANCE_RELATION, content_source_list[1]),
        rel(type_list[2], HAS_INSTANCE_RELATION, content_source_list[2])
    )

    # ===================== CONTENT =====================
    # Creates nodes
    content_list = [
        node(
            uuid=str(uuid.uuid1()),
            link='http://www.gry-online.pl/S013.asp?ID=85249',
            time=int(time.time() - 100000),
            title='Assassin\'s Creed IV i Far Cry 3 - wyniki sprzedaży gier Ubisoftu',
            image_link='http://www.gry-online.pl/galeria/html/wiadomosci/bigphotos/preview/82726815.jpg',
        ),
        node(
            uuid=str(uuid.uuid1()),
            link='http://www.tvnmeteo.pl/informacje/polska,28/na-wisle-tworzy-sie-fala-wezbraniowa,'
                 '123095,1,0.html',
            time=int(time.time() - 100000),
            title='Na Wiśle tworzy się fala wezbraniowa',
            image_link='http://r-scale-ca.dcs.redcdn.pl/scale/o2/tvn/web-content/m/p5/i/90db9da4fc'
                       '5414ab55a9fe495d555c06/6685b2b6-dce8-11e3-9205-0025b511226e.jpg?type=1&amp;'
                       'srcmode=4&amp;srcx=0/1&amp;srcy=0/1&amp;srcw=50&amp;srch=50&amp;dstw=50&amp;dsth=50',
        ),
        node(
            uuid=str(uuid.uuid1()),
            link='http://www.tvn24.pl/w-lodzi-jak-w-bombaju-totalny-chaos-na-skrzyzowaniach,429020,s.html',
            time=int(time.time() - 100000),
            title='W Łodzi jak w Bombaju. "Totalny chaos na skrzyżowaniach"',
            image_link='http://r-scale-3f.dcs.redcdn.pl/scale/o2/tvn/web-content/m/p1/i/90db9da4fc5'
                       '414ab55a9fe495d555c06/84fe9534-dcf0-11e3-9d17-0025b511229e.jpg?type=1&amp;'
                       'srcmode=4&amp;srcx=0/1&amp;srcy=0/1&amp;srcw=50&amp;srch=50&amp;dstw=50&amp;dsth=50',
        ),
        node(
            uuid=str(uuid.uuid1()),
            link='http://www.tvn24.pl/krakow,50/w-krakowie-ogloszono-pogotowie-przeciwpowodziowe,428917.html',
            time=int(time.time() - 100000),
            title='W Krakowie ogłoszono pogotowie przeciwpowodziowe',
            image_link='http://r-scale-8d.dcs.redcdn.pl/scale/o2/tvn/web-content/m/p1/i/90db9da4fc5'
                       '414ab55a9fe495d555c06/eeba57b0-dccd-11e3-8531-0025b511226e.jpg?type=1&amp;'
                       'srcmode=4&amp;srcx=0/1&amp;srcy=0/1&amp;srcw=50&amp;srch=50&amp;dstw=50&amp;dsth=50',
        )
    ]

    content_list = graph_db.create(*content_list)
    for item in content_list:
        item.add_labels(CONTENT_TYPE_MODEL_NAME, 'Node')

    # Creates instance relations
    graph_db.create(
        rel(type_list[3], HAS_INSTANCE_RELATION, content_list[0]),
        rel(type_list[3], HAS_INSTANCE_RELATION, content_list[1]),
        rel(type_list[3], HAS_INSTANCE_RELATION, content_list[2])
    )

    # Creates tag relations
    graph_db.create(
        rel(tag_list[0], HAS_TAG_RELATION, content_list[0]),
        rel(tag_list[1], HAS_TAG_RELATION, content_list[0]),
        rel(tag_list[2], HAS_TAG_RELATION, content_list[0]),
        rel(tag_list[3], HAS_TAG_RELATION, content_list[0]),
        rel(tag_list[4], HAS_TAG_RELATION, content_list[0]),

        rel(tag_list[5], HAS_TAG_RELATION, content_list[0]),
        rel(tag_list[6], HAS_TAG_RELATION, content_list[1]),
        rel(tag_list[6], HAS_TAG_RELATION, content_list[3]),
        rel(tag_list[7], HAS_TAG_RELATION, content_list[1]),
        rel(tag_list[7], HAS_TAG_RELATION, content_list[3]),

        rel(tag_list[8], HAS_TAG_RELATION, content_list[1]),
        rel(tag_list[9], HAS_TAG_RELATION, content_list[1]),
        rel(tag_list[10], HAS_TAG_RELATION, content_list[1]),
        rel(tag_list[10], HAS_TAG_RELATION, content_list[3]),
        rel(tag_list[11], HAS_TAG_RELATION, content_list[1]),

        rel(tag_list[11], HAS_TAG_RELATION, content_list[3]),
        rel(tag_list[12], HAS_TAG_RELATION, content_list[2]),
        rel(tag_list[13], HAS_TAG_RELATION, content_list[2]),
        rel(tag_list[13], HAS_TAG_RELATION, content_list[1]),
        rel(tag_list[13], HAS_TAG_RELATION, content_list[3]),

        rel(tag_list[14], HAS_TAG_RELATION, content_list[2]),
        rel(tag_list[15], HAS_TAG_RELATION, content_list[2]),
        rel(tag_list[16], HAS_TAG_RELATION, content_list[2]),
        rel(tag_list[17], HAS_TAG_RELATION, content_list[2]),
        rel(tag_list[18], HAS_TAG_RELATION, content_list[3]),

        rel(tag_list[19], HAS_TAG_RELATION, content_list[3]),
        rel(tag_list[20], HAS_TAG_RELATION, content_list[3])
    )

    batch = neo4j.WriteBatch(graph_db)
    batch.append_cypher('CREATE INDEX ON :Node(uuid)')
    batch.submit()

    print 'Graph populated successfully!'
    print 'Remember to (RE)START Lionfish server!'

