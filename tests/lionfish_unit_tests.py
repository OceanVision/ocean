import os
import sys
import re
import traceback
from py2neo import neo4j
from unit_tests_interface import UnitTests

sys.path.append(os.path.join(os.path.dirname(__file__), '../graph_workers'))
from odm_client import ODMClient


class LionfishUnitTests(UnitTests):
    def __init__(self):
        super(LionfishUnitTests, self).__init__()
        self._client = ODMClient()
        self._client.connect()
        self._batch = self._client.get_batch()
        graph_db = neo4j.GraphDatabaseService(
            # 'http://ocean-neo4j.no-ip.biz:7474/db/data/'
            'http://localhost:7474/db/data/'
        )
        self._v_read_batch = neo4j.ReadBatch(graph_db)
        self._v_write_batch = neo4j.WriteBatch(graph_db)

    # ================ G E T   B Y   U U I D ================
    def get_by_uuid__correct1(self):
        instances = self._client.get_instances(model_name='NeoUser')
        assert(len(instances) > 0)
        uuid = instances[0]['uuid']

        node = self._client.get_by_uuid(uuid)
        assert(len(node) > 0)
        assert('uuid' in node)
        assert(node['uuid'] == uuid)

        self._v_read_batch.append_cypher(
            'MATCH (e)'
            'WHERE e.uuid={uuid}'
            'RETURN (e)', {'uuid': uuid}
        )
        valid_node = self._v_read_batch.submit()[0]
        self._v_read_batch.clear()
        assert(valid_node and len(valid_node) > 0)
        assert('username' in node)
        assert(node['username'] == valid_node.get_properties()['username'])

    def get_by_uuid__correct2(self):
        instances = self._client.get_instances(model_name='ContentSource')
        assert(len(instances) > 0)
        uuid = instances[0]['uuid']

        node = self._client.get_by_uuid(uuid)
        assert(len(node) > 0)
        assert('uuid' in node)
        assert(node['uuid'] == uuid)

        self._v_read_batch.append_cypher(
            'MATCH (e)'
            'WHERE e.uuid={uuid}'
            'RETURN (e)', {'uuid': uuid}
        )
        valid_node = self._v_read_batch.submit()[0]
        self._v_read_batch.clear()
        assert(valid_node and len(valid_node) > 0)
        assert('title' in node)
        assert(node['title'] == valid_node.get_properties()['title'])

    def get_by_uuid__incorrect(self):
        instances = self._client.get_instances(model_name='NeoUser')
        assert(len(instances) > 0)
        uuid = instances[0]['uuid'].replace('a', 'e').replace('0', '1')\
            .replace('6', '7')

        node = self._client.get_by_uuid(uuid)
        assert(len(node) == 0)

    def get_by_uuid__batch(self):
        nu_instances = self._client.get_instances(model_name='NeoUser')
        cs_instances = self._client.get_instances(model_name='ContentSource')
        assert(len(nu_instances) > 0)
        assert(len(cs_instances) > 0)
        nu_uuid = nu_instances[0]['uuid']
        cs_uuid = cs_instances[0]['uuid']

        self._batch.append(self._client.get_by_uuid, nu_uuid)
        self._batch.append(self._client.get_by_uuid, cs_uuid)
        nodes = self._batch.submit()
        assert(len(nodes) == 2)
        assert(len(nodes[0]) > 0 and len(nodes[1]) > 0)
        assert('uuid' in nodes[0] and 'uuid' in nodes[1])

        self._v_read_batch.append_cypher(
            'MATCH (e)'
            'WHERE e.uuid IN {uuids}'
            'RETURN (e)', {'uuids': [nu_uuid, cs_uuid]}
        )
        results = self._v_read_batch.submit()[0]
        assert(results and len(results) > 0)
        valid_nodes = [item.values[0].get_properties() for item in results]
        self._v_read_batch.clear()
        assert('username' in nodes[0] and 'title' in nodes[1])
        assert(nodes[0] == valid_nodes[0] and nodes[1] == valid_nodes[1])

    # ================ G E T   B Y   L I N K ================
    def get_by_link__correct1(self):
        instances = self._client.get_instances(model_name='ContentSource')
        assert(len(instances) > 0)
        link = instances[0]['link']

        node = self._client.get_by_link('ContentSource', link)
        assert(len(node) > 0)
        assert('link' in node)
        assert(node['link'] == link)

        self._v_read_batch.append_cypher(
            'MATCH (e)-[]->(a)'
            'WHERE e.model_name = "ContentSource" AND a.link={link}'
            'RETURN (a)', {'link': link}
        )
        valid_node = self._v_read_batch.submit()[0]
        self._v_read_batch.clear()
        assert(valid_node and len(valid_node) > 0)
        assert('title' in node)
        assert(node['title'] == valid_node.get_properties()['title'])

    def get_by_link__correct2(self):
        instances = self._client.get_instances(model_name='Content')
        assert(len(instances) > 0)
        link = instances[0]['link']

        node = self._client.get_by_link('Content', link)
        assert(len(node) > 0)
        assert('link' in node)
        assert(node['link'] == link)

        self._v_read_batch.append_cypher(
            'MATCH (e)-[]->(a)'
            'WHERE e.model_name = "Content" AND a.link={link}'
            'RETURN (a)', {'link': link}
        )
        valid_node = self._v_read_batch.submit()[0]
        self._v_read_batch.clear()
        assert(valid_node and len(valid_node) > 0)
        assert('title' in node)
        assert(node['title'] == valid_node.get_properties()['title'])

    def get_by_link__incorrect(self):
        instances = self._client.get_instances(model_name='ContentSource')
        assert(len(instances) > 0)
        link = instances[0]['link'].replace('http', 'lol')
        node = self._client.get_by_link('ContentSource', link)
        assert(len(node) == 0)

    def get_by_link__batch(self):
        instances = self._client.get_instances(model_name='ContentSource')
        assert(len(instances) >= 2)
        link1 = instances[0]['link']
        link2 = instances[1]['link']

        self._batch.append(self._client.get_by_link, 'ContentSource', link1)
        self._batch.append(self._client.get_by_link, 'ContentSource', link2)
        nodes = self._batch.submit()
        assert(nodes and len(nodes) == 2)
        assert(nodes[0] and nodes[1])
        assert(len(nodes[0]) > 0 and len(nodes[1]) > 0)
        assert('link' in nodes[0] and 'link' in nodes[1])

        self._v_read_batch.append_cypher(
            'MATCH (e)-[]->(a)'
            'WHERE e.model_name="ContentSource" AND a.link IN {links}'
            'RETURN (a)', {'links': [link1, link2]}
        )
        results = self._v_read_batch.submit()[0]
        assert(results and len(results) > 0)
        valid_nodes = [item.values[0].get_properties() for item in results]
        self._v_read_batch.clear()
        assert(nodes[0] == valid_nodes[0] and nodes[1] == valid_nodes[1])

    # ================ G E T   M O D E L   N O D E S ================
    def get_model_nodes__regular(self):
        model_nodes = self._client.get_model_nodes()
        neo_user_uuid = ''
        content_source_uuid = ''
        for item in model_nodes:
            if item['model_name'] == 'NeoUser':
                neo_user_uuid = item['uuid']
            elif item['model_name'] == 'ContentSource':
                content_source_uuid = item['uuid']

        assert(neo_user_uuid != '' and content_source_uuid != '')

    # ================ G E T   C H I L D R E N ================
    def get_children__not_empty(self):
        model_nodes = self._client.get_model_nodes()
        uuid = ''
        for item in model_nodes:
            if item['model_name'] == 'NeoUser':
                uuid = item['uuid']
                break
        assert(uuid != '')

        nodes = self._client.get_children(uuid, '<<INSTANCE>>')
        assert(len(nodes) > 0)
        assert('uuid' in nodes[0])

        self._v_read_batch.append_cypher(
            'MATCH (e)-[r]->(a)'
            'WHERE e.uuid={uuid} AND type(r)={rel_type}'
            'RETURN (a)', {'uuid': uuid, 'rel_type': '<<INSTANCE>>'}
        )
        results = self._v_read_batch.submit()[0]
        assert(results and len(results) > 0)
        valid_nodes = [item.values[0].get_properties() for item in results]
        self._v_read_batch.clear()
        assert(len(nodes) == len(valid_nodes))
        for i in range(0, len(nodes)):
            assert(nodes[i] == valid_nodes[i])

    def get_children__not_empty_with_params(self):
        model_nodes = self._client.get_model_nodes()
        uuid = ''
        for item in model_nodes:
            if item['model_name'] == 'ContentSource':
                uuid = item['uuid']
                break
        assert(uuid != '')

        instances = self._client.get_instances(model_name='ContentSource')
        assert(len(instances) > 0)
        title = instances[0]['title']

        nodes = self._client.get_children(uuid, '<<INSTANCE>>', title=title)
        assert(len(nodes) > 0)
        assert('uuid' in nodes[0])

        self._v_read_batch.append_cypher(
            'MATCH (e)-[r]->(a)'
            'WHERE e.uuid={uuid} AND type(r)={rel_type} AND a.title={title}'
            'RETURN (a)',
            {'uuid': uuid, 'rel_type': '<<INSTANCE>>', 'title': title}
        )
        valid_node = self._v_read_batch.submit()[0].get_properties()
        self._v_read_batch.clear()
        assert(valid_node and len(valid_node) > 0)
        assert(nodes[0] == valid_node)

    def get_children__empty(self):
        model_nodes = self._client.get_model_nodes()
        uuid = ''
        for item in model_nodes:
            if item['model_name'] == 'NeoUser':
                uuid = item['uuid']
                break
        assert(uuid != '')

        nodes = self._client.get_children(uuid, '<<INSTANCE>>', title='dr')
        assert(len(nodes) == 0)

    def get_children__batch(self):
        model_nodes = self._client.get_model_nodes()
        nu_uuid = ''
        cs_uuid = ''
        for item in model_nodes:
            if item['model_name'] == 'NeoUser':
                nu_uuid = item['uuid']
            elif item['model_name'] == 'ContentSource':
                cs_uuid = item['uuid']
        assert(nu_uuid != '' and cs_uuid != '')

        nu_instances = self._client.get_instances(model_name='NeoUser')
        cs_instances = self._client.get_instances(model_name='ContentSource')
        assert(len(nu_instances) > 0 and len(cs_instances) > 0)
        title = cs_instances[0]['title']

        self._batch.append(self._client.get_children, nu_uuid, '<<INSTANCE>>')
        self._batch.append(self._client.get_children, cs_uuid, '<<INSTANCE>>',
                           title=title)
        nodes = self._batch.submit()
        assert(len(nodes) > 0)

        self._v_read_batch.append_cypher(
            'MATCH (e)-[r]->(a)'
            'WHERE e.uuid={uuid} AND type(r)={rel_type}'
            'RETURN (a)',
            {'uuid': nu_uuid, 'rel_type': '<<INSTANCE>>'}
        )
        results = self._v_read_batch.submit()[0]
        assert(results and len(results) > 0)
        valid_nodes = [item.values[0].get_properties() for item in results]
        self._v_read_batch.clear()
        assert(len(nodes[0]) == len(valid_nodes))
        for i in range(0, len(nodes[0])):
            assert(nodes[0][i] == valid_nodes[i])

    # ================ G E T   I N S T A N C E S ================
    def get_instances__not_empty(self):
        nodes = self._client.get_instances('NeoUser')
        assert(len(nodes) > 0)
        assert('uuid' in nodes[0])

        self._v_read_batch.append_cypher(
            'MATCH (e)-[r]->(a)'
            'WHERE e.model_name={model_name} AND type(r)={rel_type}'
            'RETURN (a)', {'model_name': 'NeoUser', 'rel_type': '<<INSTANCE>>'}
        )
        results = self._v_read_batch.submit()[0]
        assert(results and len(results) > 0)
        valid_nodes = [item.values[0].get_properties()
                       for item in results]
        self._v_read_batch.clear()
        assert(len(nodes) == len(valid_nodes))
        for i in range(0, len(nodes)):
            assert(nodes[i] == valid_nodes[i])

    def get_instances__empty(self):
        nodes = self._client.get_instances('MODEL')
        assert(len(nodes) == 0)

    def get_instances__batch(self):
        self._batch.append(self._client.get_instances, 'NeoUser')
        self._batch.append(self._client.get_instances, 'ContentSource')
        instances = self._batch.submit()

        assert(len(instances) == 2)
        assert(len(instances[0]) > 0 and len(instances[1]) > 0)
        assert('username' in instances[0][0] and 'title' in instances[1][0])

        nodes = instances[0] + instances[1]

        self._v_read_batch.append_cypher(
            'MATCH (e)-[r]->(a)'
            'WHERE e.model_name IN {model_names} AND type(r)={rel_type}'
            'RETURN (a)',
            {'model_names': ['NeoUser', 'ContentSource'], 'rel_type': '<<INSTANCE>>'}
        )
        results = self._v_read_batch.submit()[0]
        assert(results and len(results) > 0)
        valid_nodes = [item.values[0].get_properties()
                       for item in results]
        self._v_read_batch.clear()
        assert(len(nodes) == len(valid_nodes))
        assert(nodes == valid_nodes)

    # ================ S E T ================
    def set__correct(self):
        instances = self._client.get_instances('NeoUser')
        assert(len(instances) > 0)
        assert('uuid' in instances[0] and 'username' in instances[0])
        uuid = instances[0]['uuid']
        username = instances[0]['username']

        self._client.set(uuid, username='set_test', second_test=2)

        valid_node = self._client.get_by_uuid(uuid)
        assert('username' in valid_node and 'second_test' in valid_node)
        assert(valid_node['username'] == 'set_test'
               and valid_node['second_test'] == 2)

        self._v_read_batch.append_cypher(
            'MATCH (e)'
            'WHERE e.uuid={uuid}'
            'SET e.username={username}'
            'REMOVE e.second_test', {'uuid': uuid, 'username': username}
        )
        self._v_read_batch.submit()
        self._v_read_batch.clear()

    def set__incorrect(self):
        instances = self._client.get_instances('NeoUser')
        assert(len(instances) > 0)
        assert('uuid' in instances[0] and 'username' in instances[0])
        uuid = instances[0]['uuid'].replace('a', 'e').replace('0', '1')\
            .replace('6', '7')
        username = instances[0]['username']
        self._client.set(uuid, username='set_test', second_test=2)

        self._v_read_batch.append_cypher(
            'MATCH (e)'
            'WHERE e.uuid={uuid} OR e.second_test={second_test}'
            'RETURN (e)', {'uuid': uuid, 'second_test': 2}
        )
        results = self._v_read_batch.submit()
        self._v_read_batch.clear()
        assert(len(results) == 1 and not results[0])

    def set__batch(self):
        instances = self._client.get_instances('NeoUser')
        assert(len(instances) >= 2)
        assert('uuid' in instances[0] and 'uuid' in instances[1])
        assert('username' in instances[0] and 'username' in instances[1])
        uuid1 = instances[0]['uuid']
        uuid2 = instances[1]['uuid']
        username1 = instances[0]['username']
        username2 = instances[1]['username']

        self._batch.append(self._client.set, uuid1, username='set_test1')
        self._batch.append(self._client.set, uuid2, username='set_test2')
        self._batch.submit()

        self._batch.append(self._client.get_by_uuid, uuid1)
        self._batch.append(self._client.get_by_uuid, uuid2)
        valid_nodes = self._batch.submit()
        assert('username' in valid_nodes[0] and 'username' in valid_nodes[1])
        assert(valid_nodes[0]['username'] == 'set_test1'
               and valid_nodes[1]['username'] == 'set_test2')

        self._v_read_batch.append_cypher(
            'MATCH (e1), (e2)'
            'WHERE e1.uuid={uuid1} AND e2.uuid={uuid2}'
            'SET e1.username={username1}, e2.username={username2}',
            {'uuid1': uuid1, 'uuid2': uuid2, 'username1': username1,
             'username2': username2}
        )
        self._v_read_batch.submit()
        self._v_read_batch.clear()

    # ================ C R E A T E   &   D E L E T E   N O D E ================
    def create_and_delete_node__correct_model_name(self):
        uuid = self._client.create_node('NeoUser', username='create_node_test')
        assert(len(str(uuid)) == 36)
        node = self._client.get_by_uuid(uuid)
        assert(len(node) > 0)
        assert(node['uuid'] == uuid and node['username'] == 'create_node_test')
        self._client.delete_node(uuid)
        node = self._client.get_by_uuid(uuid)
        assert(len(node) == 0)

    def create_and_delete_node__incorrect_model_name(self):
        uuid = self._client.create_node('MODEL', username='create_node_test2')
        assert(not uuid)

        self._v_read_batch.append_cypher(
            'MATCH (e)'
            'WHERE e.username={username}'
            'RETURN (e)', {'username': 'create_node_test2'}
        )
        results = self._v_read_batch.submit()
        self._v_read_batch.clear()
        assert(len(results) == 1 and not results[0])

    def create_and_delete_node__batch(self):
        self._batch.append(
            self._client.create_node, 'NeoUser', username='create_node_test3.1'
        )
        self._batch.append(
            self._client.create_node, 'MODEL', title='create_node_test3.2'
        )
        uuids = self._batch.submit()
        assert(len(uuids) == 2)
        assert(len(str(uuids[0])) == 36 and not uuids[1])

        node = self._client.get_by_uuid(uuids[0])
        assert('uuid' in node and 'username' in node)
        assert(node['uuid'] == uuids[0] and node['username'] == 'create_node_test3.1')
        self._client.delete_node(uuids[0])
        node = self._client.get_by_uuid(uuids[0])
        assert(not node)

    # ================ C R E A T E   &   D E L E T E   R E L ================
    def create_and_delete_relationship__correct_nodes(self):
        instances = self._client.get_instances('NeoUser')
        assert(len(instances) >= 2)
        assert('uuid' in instances[0] and 'uuid' in instances[1])

        self._client.create_relationship(
            instances[0]['uuid'],
            instances[1]['uuid'],
            '<<TEST>>',
            test_param=1, test_param2='abc'
        )
        children = self._client.get_children(instances[0]['uuid'], '<<TEST>>')
        assert(len(children) == 1)
        assert('uuid' in children[0])
        assert(children[0]['uuid'] == instances[1]['uuid'])

        self._client.delete_relationship(instances[0]['uuid'], instances[1]['uuid'])
        children = self._client.get_children(instances[0]['uuid'], '<<TEST>>')
        assert(len(children) == 0)

    def create_and_delete_relationship__incorrect_nodes(self):
        instances = self._client.get_instances('NeoUser')
        assert(len(instances) >= 2)
        assert('uuid' in instances[0] and 'uuid' in instances[1])

        self._client.create_relationship(
            instances[0]['uuid'].replace('a', 'e').replace('0', '1')
            .replace('6', '7'),
            instances[1]['uuid'].replace('a', 'e').replace('0', '1')
            .replace('6', '7'),
            '<<TEST>>',
            test_param=1, test_param2='abc'
        )
        children = self._client.get_children(instances[0]['uuid'], '<<TEST>>')
        assert(len(children) == 0)

    def create_and_delete_relationship__batch(self):
        nu_instances = self._client.get_instances('NeoUser')
        cs_instances = self._client.get_instances('ContentSource')
        assert(len(nu_instances) >= 2 and len(cs_instances) >= 2)
        assert('uuid' in nu_instances[0] and 'uuid' in nu_instances[1])
        assert('uuid' in cs_instances[0] and 'uuid' in cs_instances[1])

        self._batch.append(
            self._client.create_relationship,
            nu_instances[0]['uuid'],
            nu_instances[1]['uuid'],
            '<<TEST1>>',
            test_param=1, test_param2='abc'
        )
        self._batch.append(
            self._client.create_relationship,
            cs_instances[0]['uuid'],
            cs_instances[1]['uuid'],
            '<<TEST2>>',
            test_param=1, test_param2='def'
        )
        self._batch.submit()
        self._batch.append(
            self._client.get_children, nu_instances[0]['uuid'], '<<TEST1>>'
        )
        self._batch.append(
            self._client.get_children, cs_instances[0]['uuid'], '<<TEST2>>'
        )
        children = self._batch.submit()
        assert(len(children) == 2)
        assert(len(children[0]) == 1 and len(children[1]) == 1)
        assert('uuid' in children[0][0] and 'uuid' in children[1][0])
        assert(children[0][0]['uuid'] == nu_instances[1]['uuid'])
        assert(children[1][0]['uuid'] == cs_instances[1]['uuid'])

        self._batch.append(
            self._client.delete_relationship,
            nu_instances[0]['uuid'],
            nu_instances[1]['uuid']
        )
        self._batch.append(
            self._client.delete_relationship,
            cs_instances[0]['uuid'],
            cs_instances[1]['uuid']
        )
        self._batch.submit()
        self._batch.submit()
        self._batch.append(
            self._client.get_children, nu_instances[0]['uuid'], '<<TEST1>>'
        )
        self._batch.append(
            self._client.get_children, cs_instances[0]['uuid'], '<<TEST2>>'
        )
        children = self._batch.submit()
        assert(len(children) == 2)
        assert(len(children[0]) == 0 and len(children[1]) == 0)

if __name__ == "__main__":
    unit_tests = LionfishUnitTests()
    unit_tests.run()
