"""
Exemplary data for neo4j database
Note : wipes database !
Connection done using RESTApi and wrapper for python py2neo
"""

from py2neo import neo4j
from py2neo import node, rel

if __name__ == "__main__":
    # Create connection
    graph_db = neo4j.GraphDatabaseService("http://localhost:7474/db/data/")

    # UNCOMMENT !!
    print "This script will *ERASE ALL NODES AND RELATIONS IN NEO4J DATABASE*, press enter to proceed"
    enter = raw_input()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher("START n=node(*) return count(n);")
    print "Nodes in graph initially ",my_batch.submit()
    print "Erasing nodes and relations"

    my_batch = neo4j.WriteBatch(graph_db)
    my_batch.append_cypher("start r=relationship(*) delete r;")
    my_batch.append_cypher("start n=node(*) WHERE ID(n) <> 0 delete n ;") # fix: do not delete the root
    my_batch.submit()

    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher("START n=node(*) return count(n);")
    result = my_batch.submit()
    print "Nodes in graph erased. Sanity check : ",result

    if result[0]!=1:
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
        node (
            app_label = "rss", name = "rss:NewsWebsite", model_name = "NewsWebsite"
        ),
        node (
            app_label = "rss", name = "rss:NeoUser", model_name = "NeoUser"
        ),
        node (
            app_label = "rss", name = "rss:News", model_name = "News"
        )
    ]
    types = graph_db.create(*types)
    # Create type relations
    graph_db.create (
        rel ( root, HAS_TYPE_RELATION, types[0] ),
        rel ( root, HAS_TYPE_RELATION, types[1] ),
        rel ( root, HAS_TYPE_RELATION, types[2] )
    )

    ### Add users ###
    # Create nodes
    users = [
        node(label=USER_LABEL, username="kudkudak"),
        node(label=USER_LABEL,username="konrad")
    ]
    users = graph_db.create(*users)
    # Create instance relations
    graph_db.create (
        rel ( types[1], HAS_INSTANCE_RELATION, users[0] ),
        rel ( types[1], HAS_INSTANCE_RELATION, users[1] )
    )

    # 1.9 doesnt support labels!
    #map(lambda u: u.add_labels(USER_LABEL),users) # Add labels
    #print [x for x in  graph_db.find(USER_LABEL)] # Sanity check,

    ### Add websites ###
    # Create nodes
    websites = [
        node(label=NEWS_WEBSITE_LABEL,url="www.antyweb.pl"),
        node(label=NEWS_WEBSITE_LABEL,url="www.onet.pl"),
        node(label=NEWS_WEBSITE_LABEL,url="www.wp.pl")
    ]
    websites = graph_db.create(*websites)
    # Create instance relations
    graph_db.create (
        rel ( types[0], HAS_INSTANCE_RELATION, websites[0] ),
        rel ( types[0], HAS_INSTANCE_RELATION, websites[1] ),
        rel ( types[0], HAS_INSTANCE_RELATION, websites[2] )
    )

    #map(lambda w: w.add_labels(NEWS_WEBSITE_LABEL),websites) # Add labels
    #print [x for x in  graph_db.find(NEWS_WEBSITE_LABEL)] # Sanity check

    news = [
        node (
        label = NEWS_LABEL,
        url="http://konflikty.wp.pl/kat,106090,title,Nowe-smiglowce-USA-"\
    "Wielki-projekt-zbrojeniowy-w-cieniu-budzetowych-ciec,wid,16116470,wiadomosc.html?ticaid=111908"
        )
         ,node (
            label = NEWS_LABEL,
            url= "www.news.pl"
        )
    ]

    news = graph_db.create(*news) # Create nodes in graph database
    #map(lambda w: w.add_labels(NEWS_LABEL),news) # Add labels

    graph_db.create (
        rel(users[0], SUBSCRIBES_TO_RELATION, websites[2]),
        rel(users[0], SUBSCRIBES_TO_RELATION, websites[1]),
        rel(users[1], SUBSCRIBES_TO_RELATION, websites[1]),
        rel(websites[2],PRODUDES_RELATION, news[0] ),
        rel(websites[1],PRODUDES_RELATION, news[1] )
    )

    graph_db.create (
        rel ( types[2], HAS_INSTANCE_RELATION, news[0]),
        rel ( types[2], HAS_INSTANCE_RELATION, news[1])
    )

    print "Graph populated successfully"
