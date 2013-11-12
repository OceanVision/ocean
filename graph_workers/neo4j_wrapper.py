# TODO: implement wrapper (in 3rd iteration), which will check privileges of GraphWorker
# when writing to database and also wrap basic access patterns


""" Quick note about neo4j wrapper :
every node creation copies graph_db to inside of the class
when called update_properties it will use graph_db.
So if graph_db is closed - it fails.
"""



import datetime
from datetime import datetime, timedelta
import pytz
from dateutil import parser
from pytz import timezone
from py2neo import neo4j
from py2neo import node, rel
import py2neo
import time

def get_type_metanode(graph_db, model_name):
    """
        @returns Metanode representing given "model_name"
    """
    my_batch = neo4j.ReadBatch(graph_db)
    my_batch.append_cypher(
        """
        START v=node(0)
        MATCH (v)-[]->(n)
        WHERE has(n.model_name)
        RETURN n
        """
    )
    results = my_batch.submit()
    metanode = None
    for node in results[0]:
        if node.n.get_properties()["model_name"] == model_name:
            metanode = node.n
            break
    return metanode

def pubdate_to_datetime(pubdate):
    """ Wrapper for annoying conversion"""
    # Different time formats. Propses .. omg
    #d = parser.parse(pubdate)
    #d = d.replace(tzinfo=timezone("GMT"))
    #return d
    # Found better solution, but keeping the code for now
    tok = pubdate.replace(",", "").replace(":", " ").split(" ")
    try:
        d = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z") if \
            len(tok[3]) > 2 else time.strptime(pubdate, "%a, %d %b %y %H:%M:%S %Z")
        return d.replace(tzinfo=timezone("GMT")) # make timezone aware for robustness
    except:
        # PYTHON 2.7 DOESNT SUPPORT %z DIRECTIVE !!!.. omg, official documentation..
        try:
            offset = int(pubdate[-5:])
            delta = timedelta(hours=offset/100)
            d = datetime.strptime(pubdate[:-6], "%a, %d %b %Y %H:%M:%S") if \
                len(tok[3]) > 2 else datetime.strptime(pubdate[:-6], "%a, %d %b %y %H:%M:%S")
            d -= delta
            return d.replace(tzinfo=timezone("GMT")) # make timezone aware for robustness
        except Exception, e:
            print e
            print pubdate
            raise Exception("Wrong date format")



def datetime_to_pubdate(d):
    """
    @returns "%a, %d %b %Y %H:%M:%S %Z"
    """

    return d.strftime("%a, %d %b %Y %H:%M:%S %Z") #unify strftime
