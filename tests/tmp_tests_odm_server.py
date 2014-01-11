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
    cs = db.get_all_instances(model_name="ContentSource")
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

    assert(len(cl.get_type_nodes()) >= 3)

    for t in cl.get_type_nodes():
        if t["model_name"] == "ContentSource":
            print "Found type ", t
            type_content_source = t

    ### Retrieve all instances by get_all_children and after that ###
    ### recieve only the first one ###
    assert(type_content_source is not None)

    all_children = db.get_all_children(parent_uuid=type_content_source["uuid"], rel_name="<<INSTANCE>>")
    
    assert(len(all_children) > 2)

    picked_child = all_children[0]
    
    picked_child_queried = db.get_all_children(parent_uuid=type_content_source["uuid"], 
        rel_name="<<INSTANCE>>", link=picked_child["link"])

    print picked_child
    print picked_child_queried

    assert(len(picked_child_queried) == 1 and \
        picked_child_queried[0]["uuid"] == picked_child["uuid"])
    

        

#     print cl.get_all_children("1814d088-7a2 f-11e3-8ac6-485d60f20495", 

