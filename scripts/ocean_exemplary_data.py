"""
Exemplary data for neo4j database
Note : wipes database !
Connection done using RESTApi and wrapper for python py2neo
"""

from py2neo import neo4j
from py2neo import node, rel
import time

if __name__ == "__main__":
    # Create connection
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # UNCOMMENT !!
    print "This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*, press enter to proceed"
    enter = raw_input()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher("START n=node(*) return count(n);")
    print "Nodes in graph initially ", my_batch.submit()
    print "Erasing nodes and relations"

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher("start r=relationship(*) delete r;")
    my_batch.append_cypher("start n=node(*) WHERE ID(n) <> 0 delete n ;")  # fix: do not delete the root
    my_batch.submit()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher("START n=node(*) return count(n);")
    result = my_batch.submit()
    print "Nodes in graph erased. Sanity check : ", result

    if result[0] != 1:
        raise Exception("Not erased graph properly")
        exit(1)

    USER_LABEL = "__user__"
    NEWS_WEBSITE_LABEL = "__news_website__"
    NEWS_LABEL = "__news__"

    HAS_TYPE_RELATION = "<<TYPE>>"
    HAS_INSTANCE_RELATION = "<<INSTANCE>>"
    SUBSCRIBES_TO_RELATION = "__subscribes_to__"
    PRODUDES_RELATION = "__produces__"

    root = graph_db.node(0)

    ### Add webservice types ###
    # Create nodes
    types = [
        node(
            app_label="rss", name="rss:NewsWebsite", model_name="NewsWebsite"
        ),
        node(
            app_label="rss", name="rss:NeoUser", model_name="NeoUser"
        ),
        node(
            app_label="rss", name="rss:News", model_name="News"
        )
    ]
    types = graph_db.create(*types)
    # Create type relations
    graph_db.create(
        rel(root, HAS_TYPE_RELATION, types[0]),
        rel(root, HAS_TYPE_RELATION, types[1]),
        rel(root, HAS_TYPE_RELATION, types[2])
    )

    ### Add users ###
    # Create nodes
    users = [
        node(label=USER_LABEL, username="kudkudak"),
        node(label=USER_LABEL, username="konrad"),
        node(label=USER_LABEL, username="brunokam"),
        node(label=USER_LABEL, username="szymon")
    ]
    users = graph_db.create(*users)
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
    # Create nodes
    websites = [
        node(label=NEWS_WEBSITE_LABEL, link="http://www.gry-online.pl/rss/news.xml",
             title="GRY-OnLine Wiadomosci", description="Najnowsze Wiadomosci",
             image_width="144", image_height="18", image_link="http://www.gry-online.pl/S012.asp",
             image_url="http://www.gry-online.pl/rss/rss_logo.gif", language="pl",
             last_updated=int(time.time() - 100000), source_type="rss"
        ),
        node(label=NEWS_WEBSITE_LABEL, link="http://wiadomosci.wp.pl/kat,1329,ver,rss,rss.xml",
             title="Wiadomosci WP - Wiadomosci - Wirtualna Polska",
             description="Wiadomosci.wp.pl to serwis, dzieki ktoremu mozna zapoznac sie z biezaca sytuacja w kraju i na"
                         " swiecie.",
             image_width="70", image_height="28", image_link="http://wiadomosci.wp.pl",
             image_url="http://i.wp.pl/a/i/finanse/logozr/WP.gif", language="pl",
             last_updated=int(time.time() - 1000000), source_type="rss"
        ),
        node(label=NEWS_WEBSITE_LABEL, link="http://www.tvn24.pl/najwazniejsze.xml",
             title="TVN24.pl - Wiadomosci z kraju i ze swiata - najnowsze informacje w TVN24",
             description="Czytaj najnowsze informacje i ogladaj wideo w portalu informacyjnym TVN24! U nas zawsze "
                         "aktualne wiadomosci z kraju, ze swiata, relacje na zywo i wiele wiecej.", language="pl",
             last_updated=int(time.time() - 100000), source_type="rss")
    ]
    websites = graph_db.create(*websites)
    # Create instance relations
    graph_db.create(
        rel(types[0], HAS_INSTANCE_RELATION, websites[0]),
        rel(types[0], HAS_INSTANCE_RELATION, websites[1]),
        rel(types[0], HAS_INSTANCE_RELATION, websites[2])
    )

    #map(lambda w: w.add_labels(NEWS_CHANNELS_LABEL),channels) # Add labels
    #print [x for x in  graph_db.find(NEWS_CHANNELS_LABEL)] # Sanity check


    # Adding news is working, and therefore we do not need to populate graph artificially with news
    graph_db.create(
        rel(users[0], SUBSCRIBES_TO_RELATION, websites[2]),
        rel(users[0], SUBSCRIBES_TO_RELATION, websites[1]),
        rel(users[1], SUBSCRIBES_TO_RELATION, websites[1])
   )


    #news = [
    #node(
    #    label=NEWS_LABEL, link="http://konflikty.wp.pl/kat,106090,title,Nowe-smiglowce-USA-Wielki-projekt-"
    #                           "zbrojeniowy-w-cieniu-budzetowych-ciec,wid,16116470,wiadomosc.html?ticaid=111908",
    #    title="Wypadek busa w Egipcie. Rannych zostalo dwoch Polakow",
    #    description="Szesciu cudzoziemcow, w tym dwoch Polakow, zostalo rannych w wypadku drogowym w Egipcie. "
    #                "Do zdarzenia doszlo na drodze miedzy Kairem a Aleksandria - informuje serwis ruvr.ru.",
    #    guid="http://wiadomosci.wp.pl/kat,1329,title,Wypadek-busa-w-Egipcie-Rannych-zostalo-dwoch-Polakow,wid,"
    #         "16151839,wiadomosc.html"
    #)
    #, node(
    #    label=NEWS_LABEL, link="http://www.tvn24.pl/naukowcy-slady-polonu-w-ciele-arafata-sugeruja-udzial-osob-"
    #                           "trzecich,369594,s.html",
    #    title="Naukowcy: slady polonu w ciele Arafata sugeruja udzial osob trzecich",
    #    description="Palestynskiego lidera otruto w roku 2004.",
    #    guid="http://www.tvn24.pl/naukowcy-slady-polonu-w-ciele-arafata-sugeruja-udzial-osob-trzecich,369594,s.html"
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

    print "Graph populated successfully"

