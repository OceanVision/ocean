""" Temporary file - testing odm, we can rewrite
    it later to unit tests or something like this
"""


import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

sys.path.append(os.path.join(os.path.dirname(__file__), "../graph_workers"))

from odm_server import DatabaseManager
from odm_client import ODMClient


#TODO: fill in performance unit test
def massing_add_delete():
    pass  #asserts

def basic_tests_local():
    ### Create Objects ###
    db = DatabaseManager()
    cs = db.get_instances(model_name="ContentSource", children_params={})
    assert(len(cs) > 0)

def basic_tests():
    
    ### Connect ###
    cl = ODMClient()
    cl.connect()

    print "0. get instance by params"
    
    assert(cl.get_instances(model_name="NeoUser", username="kudkudak")[0]["username"]=="kudkudak")
    cs = cl.get_instances(model_name="ContentSource")

    print "1. Change one instance"
    ### Change one instance and see if change has occured ### 
    uuid_0 = cs[0]['uuid']
    previous_image_height = cs[0]['image_height']
    cl.set(uuid_0, {'image_height': 100})
    assert(cl.get_by_uuid(uuid_0)['image_height'] == 100)
    cl.set(uuid_0, {'image_height': previous_image_height})
    assert(cl.get_by_uuid(uuid_0)['image_height'] == previous_image_height)
    


    ### Get type nodes and get all children of <<TYPE>> = "ContentSource"
    print "2 and 3. Get model node and check get_children"
    type_content_source = None
    assert(len(cl.get_model_nodes()) >= 3)
    print cl.get_model_nodes()

    for t in cl.get_model_nodes():
        if t["model_name"] == "ContentSource":
            print "Found type ", t
            type_content_source = t

    ### Retrieve all instances by get_all_children and after that ###
    ### recieve only the first one ###
    assert(type_content_source is not None)
    all_children = cl.get_children(node_uuid=type_content_source["uuid"],
                                       rel_type="<<INSTANCE>>")
    assert(len(all_children) > 2)
    

    picked_child = all_children[0]
    picked_child_queried = cl.get_children(node_uuid=type_content_source["uuid"],
        rel_type="<<INSTANCE>>", children_params={'link': picked_child["link"]})
    assert(len(picked_child_queried) == 1 and \
        picked_child_queried[0]["uuid"] == picked_child["uuid"])
    


    print "4. Test adding nodes"
    ### Testing adding nodes ###
    initial_content_nodes = len(cl.get_instances(model_name="Content"))
    try:
        print "First content ",cl.get_instances(model_name="Content")[0]
    except:
        pass
    print "Initially content nodes ", initial_content_nodes 
    uuid1=cl.add_node(model_name="Content", node_params={})["uuid"]
    uuid2=cl.add_node(model_name="Content", node_params={})["uuid"]
    uuid3=cl.add_node(model_name="Content", node_params={})["uuid"]
    after_adding_content_nodes = len(cl.get_instances(model_name="Content"))
    print "After adding content nodes ", after_adding_content_nodes 
    assert(after_adding_content_nodes-initial_content_nodes == 3)
    cl.delete_node(node_uuid=uuid1)
    cl.delete_node(node_uuid=uuid2)
    cl.delete_node(node_uuid=uuid3)
    after_del_content_nodes = len(cl.get_instances(model_name="Content"))
    assert(after_del_content_nodes-initial_content_nodes == 0)
#     print cl.get_all_children("1814d088-7a2 f-11e3-8ac6-485d60f20495",

    print "5. Test query execution"
    ### Test execute query ###
    cypher_query = """
            START root=node(0)
            MATCH root-[rel:`<<TYPE>>`]->news_type-[rel2:`<<INSTANCE>>`]->news
            WHERE news_type.model_name="Content"
            RETURN news
            ORDER BY news.pubdate_timestamp DESC
            LIMIT 100
        """

    results = cl.execute_query(query_string = cypher_query, query_params = {})

    print len(results)

    print '6. Test batch execution'
    res1 = cl.get_instances('NeoUser')
    res2 = cl.get_by_link('Website', 'http://www.gry-online.pl/')

    batch = cl.get_batch()
    batch.append(cl.get_instances, ['NeoUser'])
    batch.append(cl.get_by_link, ['Website', 'http://www.gry-online.pl/'])
    res3 = batch.execute()

    assert (res1 == res3[0])
    assert (res2 == res3[1])
    print 'OK'


def test_utf():
    db = DatabaseManager()
    
    cl = ODMClient()
    print "Connecting"
    cl.connect()

    print "Fetching"

    website = cl.get_instances(model_name="ContentSource")[1]

    print website

    contents = cl.get_children(website["uuid"], "__produces__")
    
    print len(contents)

    news = contents[0]

    print type(news["title"])
    print "Checking ",news["title"]
    print type(news["title"].encode("utf-8"))

    existing_nodes_title = len(cl.get_children\
                (node_uuid=website["uuid"], rel_type="__produces__" , 
                title=unicode(news["title"])))
        

    print existing_nodes_title
    assert(existing_nodes_title == 1)



if __name__ == "__main__":
    #test_utf()
    basic_tests()

