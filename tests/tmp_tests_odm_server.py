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

if __name__ == "__main__":
    
    ### Create Objects ###
    db = DatabaseManager()
    cs = db.get_instances(model_name="ContentSource", children_params={})
    assert(len(cs) > 0) 
    
    ### Connect ###
    cl = ODMClient()
    cl.connect()


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
    all_children = db.get_children(node_uuid=type_content_source["uuid"],
                                       rel_type="<<INSTANCE>>")
    assert(len(all_children) > 2)
    

    picked_child = all_children[0]
    picked_child_queried = db.get_children(node_uuid=type_content_source["uuid"],
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


# TODO: add asserts
#     batch = cl.get_batch()
#     batch.append('get_instances', model_name='NeoUser')
#     batch.append('get_instances', model_name='Content')
#     batch.append('add_node', model_name='Content', node_params={})
#     print 'Batch execute:'
#     res1 = batch.execute()
#     uuid_1 = res1[2]['uuid']
#     batch.append('delete_node', node_uuid=uuid_1)
#     res2 = batch.execute()
#     for item in res1:
#         print item
#     print res2[0]
# 

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
    

