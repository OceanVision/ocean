""" Temporary file - testing odm, we can rewrite
    it later to unit tests or something like this
"""


import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

sys.path.append(os.path.join(os.path.dirname(__file__), "../graph_workers"))

from odm_server import DatabaseManager
from odm_client import ODMClient

if __name__ == "__main__":
    
    ### Create Objects ###
    db = DatabaseManager()
    cs = db.get_instances(model_name="ContentSource", children_params={})
    print "Fetched ContentSources"
    print cs 
    
    ### Get not existing node ###
    print db.get_by_uuid(node_uuid="x")
    
    ### Connect ###
    cl = ODMClient()
    cl.connect()

    ### Get all instances of ContentSource ###
    print cs
    uuid_0 = cs[0]['uuid']

    ### Change one instance and see if change has occured ###
    cl.set(uuid_0, {'image_height': 100})

    print "Specific node:"
    print cl.get_by_uuid(uuid_0)

    ### Get type nodes and get all children of <<TYPE>> = "ContentSource"
    print ".."

    type_content_source = None

    assert(len(cl.get_model_nodes()) >= 3)

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
        rel_type="<<INSTANCE>>", children_params={'link': picked_child["link"],
                                                  'language': 'pl'})

    print picked_child
    print picked_child_queried

    assert(len(picked_child_queried) == 1 and \
        picked_child_queried[0]["uuid"] == picked_child["uuid"])
    

    ### Testing adding nodes ###
    initial_content_nodes = len(cl.get_instances(model_name="Content"))
    print "Initially content nodes ", initial_content_nodes 
    cl.add_node(model_name="Content", node_params={})
    cl.add_node(model_name="Content", node_params={})
    cl.add_node(model_name="Content", node_params={}) 
    after_adding_content_nodes = len(cl.get_instances(model_name="Content"))
    print "After adding content nodes ", after_adding_content_nodes 
    assert(after_adding_content_nodes-initial_content_nodes == 3)
#     print cl.get_all_children("1814d088-7a2 f-11e3-8ac6-485d60f20495", 

    batch = cl.get_batch()
    batch.append('get_instances', model_name='NeoUser')
    batch.append('get_instances', model_name='Content')
    batch.append('add_node', model_name='Content', node_params={})
    print 'Batch execute:'
    res1 = batch.execute()
    uuid_1 = res1[2]['uuid']
    batch.append('delete_node', node_uuid=uuid_1)
    res2 = batch.execute()
    for item in res1:
        print item
    print res2[0]