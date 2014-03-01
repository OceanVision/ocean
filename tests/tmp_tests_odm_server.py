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


def basic_tests():
    ### Connect ###
    cl = ODMClient()
    cl.connect()

    model_nodes = cl.get_model_nodes()
    neo_user_uuid = ''
    content_source_uuid = ''
    for item in model_nodes:
        if item['model_name'] == 'NeoUser':
            neo_user_uuid = item['uuid']
        elif item['model_name'] == 'ContentSource':
            content_source_uuid = item['uuid']

    assert(neo_user_uuid != '' and content_source_uuid != '')
    print 'get_model_nodes: OK'

    instances = cl.get_instances(model_name='ContentSource')
    assert(len(instances) > 0)
    assert(cl.get_children(node_uuid=content_source_uuid, rel_type='<<INSTANCE>>') == instances)
    print 'get_instances: OK'
    print 'get_children all: OK'

    assert(cl.get_children(node_uuid=neo_user_uuid, rel_type='<<INSTANCE>>',
                           username='brunokam')[0]['username'] == 'brunokam')
    print 'get_children with params: OK'

    ### Change one instance and see if change has occured ### 
    uuid_0 = instances[0]['uuid']
    previous_image_height = instances[0]['image_height']
    cl.set(uuid_0, {'image_height': 100})
    assert(cl.get_by_uuid(uuid_0)['image_height'] == 100)
    cl.set(uuid_0, {'image_height': previous_image_height})
    assert(cl.get_by_uuid(uuid_0)['image_height'] == previous_image_height)
    print 'set: OK'
    
    return

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
    cl.connect()

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
    # test_utf()
    basic_tests()

