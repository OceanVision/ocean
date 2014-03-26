"""
Lionfish (formerly Ocean Database Manager)

general idea is as follows: ODM have many get procedures, however only one way
to add or set node/rel (add_node, set, add_rel,  del_rel, del_node)

get_by_uuid will be cached, as well as multiget. Other get procedures are
not guaranteed to be cached
"""

from py2neo import neo4j
import uuid
import os
import socket
import logging
from threading import Thread
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../graph_workers'))
from graph_defines import *
from graph_utils import *

HOST = ''
PORT = 21

# Defining levels to get rid of other loggers
info_level = 100
error_level = 200

logging.basicConfig(level=info_level)
logger = logging.getLogger(__name__ + '_ocean')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),
                                           '../logs/odm_server.log'))
ch_file.setLevel(info_level)
logger.addHandler(ch_file)


class DatabaseManager(object):
    """ Driver for Neo4j database """
    def __init__(self):
        """ Creates DatabaseManager driver """
        logger.log(info_level, 'Created DatabaseManager object')
        self._graph_db = neo4j.GraphDatabaseService(
            'http://localhost:16/db/data/'
            # 'http://localhost:7474/db/data/'
        )
        self._uuid_images = dict()
        self._model_name_images = dict()

        self._init_uuid_images()
        self._init_model_name_images()

    def _init_model_name_images(self):
        self._model_name_images.clear()
        query_string = '' \
            'MATCH (e:Model)' \
            'RETURN e.model_name, e.uuid'
        query_results = self._execute_query(query_string)
        for record in query_results:
            key = record[0]
            value = record[1]
            self._model_name_images[key] = value

    def _init_uuid_images(self):
        self._uuid_images.clear()
        query_string = \
            'MATCH (e:Node)' \
            'RETURN e.uuid, id(e)'
        query_results = self._execute_query(query_string)
        for record in query_results:
            key = record[0]
            value = record[1]
            self._uuid_images[key] = value

    @error_handle_odm
    def _str(self, dictionary):
        string = '{'
        for key, value in dictionary.iteritems():
            string += '{0}: {1}, '.format(
                key, json.dumps(value, ensure_ascii=False)
            )

        if len(string) > 1:
            string = string[:len(string) - 2]
        return string + '}'

    @error_handle_odm
    def _execute_query(self, query_string, **query_params):
        """
        Executes query and returns results as python dictionaries
        @param query_string string
        @param multi_value bool
        @param query_params dictionary
        """
        # Executes cypher query
        cypher_query = neo4j.CypherQuery(self._graph_db, unicode(query_string))
        query_results = cypher_query.execute(**query_params)

        results = []
        for result in query_results:
            values = []
            for value in result.values:
                if value.__class__.__name__ in ('Node', 'Relationship'):
                    values.append(value.get_properties())
                else:
                    values.append(value)
            results.append(values)
        return results

    @error_handle_odm
    def _run_query(self, query_string, **query_params):
        """
        Runs query only
        @param query_string
        @param query_params
        """
        cypher_query = neo4j.CypherQuery(self._graph_db, unicode(query_string))
        cypher_query.run(**query_params)

    @error_handle_odm
    def get_by_uuid(self, node_uuid_list):
        # Prepares MATCH statement
        match_str = ''
        for i, item in enumerate(node_uuid_list):
            match_str += 'OPTIONAL MATCH (e{0}:Node {{uuid: {1}}}) '\
                .format(i, json.dumps(item))

        # Prepares RETURN statement
        return_str = 'RETURN DISTINCT '
        for i in range(0, len(node_uuid_list)):
            return_str += '(e{0}), '.format(i)
        return_str = return_str[:len(return_str) - 2]

        # Builds query and gets results
        query_string = match_str + return_str
        results = self._execute_query(query_string)
        return results[0]

    @error_handle_odm
    def get_by_link(self, node_list):
        # Prepares MATCH statement
        match_str = ''
        for i, item in enumerate(node_list):
            match_str += 'OPTIONAL MATCH (e{0}:{1} {{link: {2}}}) '\
                .format(i, item['model_name'], json.dumps(item['link']))

        # Prepares RETURN statement
        return_str = 'RETURN DISTINCT '
        for i in range(0, len(node_list)):
            return_str += '(e{0}), '.format(i)
        return_str = return_str[:len(return_str) - 2]

        # Builds query and gets results
        query_string = match_str + return_str
        results = self._execute_query(query_string)
        return results[0]

    @error_handle_odm
    def get_model_nodes(self):
        # Builds query and gets results
        query_string = \
            'MATCH (e:Model) ' \
            'RETURN (e)'
        return self._execute_query(query_string)

    @error_handle_odm
    def get_children(self, node_list):
        # Prepares query
        query_string = ''
        for i, item in enumerate(node_list):
            query_string += \
                'MATCH (e:Node {{uuid: {0}}})-[r:`{1}`]->(a:Node {2}) ' \
                'RETURN (a) '.format(json.dumps(item['uuid']), item['rel_type'],
                                     self._str(item['children_params']))
            if i < len(node_list) - 1:
                query_string += 'UNION ALL MATCH (a:Root) RETURN (a) UNION ALL '

        # Gets results and extracts them from default list
        raw_results = self._execute_query(query_string)
        results = [[]]
        no = 0
        for item in raw_results:
            if 'root' not in item[0]:
                results[no].append(item[0])
            else:
                results.append([])
                no += 1
        return results

    @error_handle_odm
    def get_instances(self, model_name_list):
        # Prepares query
        query_string = ''
        for i, item in enumerate(model_name_list):
            query_string += \
                'MATCH (e:Model {{model_name: {0}}})-[:`<<INSTANCE>>`]->(a:{1}) ' \
                'RETURN (a) '.format(json.dumps(item), item)
            if i < len(model_name_list) - 1:
                query_string += 'UNION ALL MATCH (a:Root) RETURN (a) UNION ALL '

        # Gets results and extracts them from default list
        raw_results = self._execute_query(query_string)
        results = [[]]
        no = 0
        for item in raw_results:
            if 'root' not in item[0]:
                results[no].append(item[0])
            else:
                results.append([])
                no += 1
        return results

    @error_handle_odm
    def set(self, node_list):
        # Prepares MATCH statement
        match_str = 'MATCH '
        for i, item in enumerate(node_list):
            match_str += '(e{0}:Node {{uuid: {1}}}), '\
                .format(i, json.dumps(item['uuid']))
        match_str = match_str[:len(match_str) - 2] + ' '

        # Prepares SET statement
        set_str = 'SET '
        for i, node in enumerate(node_list):
            for key, value in node['params'].iteritems():
                set_str += 'e{0}.{1} = {2}, '\
                    .format(i, key, json.dumps(value, ensure_ascii=False))
        set_str = set_str[:len(set_str) - 2]

        # Builds query and runs it
        query_string = match_str + set_str
        self._run_query(query_string)

    @error_handle_odm
    def create_nodes(self, node_list):
        # Prepares params
        fail_list = []
        for i, item in enumerate(node_list):
            model_name = item['model_name']
            if model_name not in self._model_name_images:
                fail_list.append(i)
                continue

            # Default values loaded from graph_defines
            params = dict(GRAPH_MODELS[model_name]) \
                if model_name in GRAPH_MODELS else {}
            params.update(item['params'])
            params['uuid'] = str(uuid.uuid1())
            item['params'] = params

        # Removes the nodes with incorrect model names
        deleted_count = 0
        for i in fail_list:
            node_list.pop(i - deleted_count)
            deleted_count += 1

        # All given uuids are bad
        if len(node_list) == 0:
            node_uuid_list = []
            for i in range(0, len(fail_list)):
                node_uuid_list.append(None)
            return node_uuid_list

        # Prepares MATCH statement
        match_str = 'MATCH '
        for i, item in enumerate(node_list):
            match_str += '(e{0}:Model {{model_name: {1}}}), '\
                .format(i, json.dumps(item['model_name']))
        match_str = match_str[:len(match_str) - 2] + ' '

        # Prepares CREATE statement
        create_str = 'CREATE UNIQUE '
        for i, item in enumerate(node_list):
            create_str += '(e{0})-[:`{1}`]->(a{0}:Node:{2} {3}), '\
                .format(i, item['rel_type'], item['model_name'],
                        self._str(item['params']))
        create_str = create_str[:len(create_str) - 2] + ' '

        # Prepares RETURN statement
        return_str = 'RETURN '
        for i in range(0, len(node_list)):
            return_str += 'id(a{0}), '.format(i)
        return_str = return_str[:len(return_str) - 2]

        # Builds query and gets results
        query_string = match_str + create_str + return_str
        results = self._execute_query(query_string)

        # Prepares the list of uuids to be returned
        node_uuid_list = []
        for i, item in enumerate(node_list):
            self._uuid_images[item['params']['uuid']] = results[0][i]
            node_uuid_list.append(item['params']['uuid'])

        # Fills the list of uuids with broken requests
        for i in fail_list:
            node_uuid_list.insert(i, None)

        return node_uuid_list

    @error_handle_odm
    def delete_nodes(self, node_uuid_list):
        # Prepares params
        fail_list = []
        for i, item in enumerate(node_uuid_list):
            if item not in self._uuid_images:
                fail_list.append(i)
                continue

        # Removes the incorrect uuid
        deleted_count = 0
        for i in fail_list:
            node_uuid_list.pop(i - deleted_count)
            deleted_count += 1

        # All given uuids are bad
        if len(node_uuid_list) == 0:
            return

        # Prepares MATCH statement
        match_str = 'MATCH '
        for i, item in enumerate(node_uuid_list):
            match_str += '(e{0}:Node {{uuid: {1}}})-[r{0}]-(), '\
                .format(i, json.dumps(item))
        match_str = match_str[:len(match_str) - 2] + ' '

        # Prepares DELETE statement
        delete_str = 'DELETE '
        for i in range(0, len(node_uuid_list)):
            delete_str += '(e{0}), (r{0}), '.format(i)
        delete_str = delete_str[:len(delete_str) - 2]

        # Builds query and runs it
        query_string = match_str + delete_str
        self._run_query(query_string)

        # Removes uuids of deleted nodes from cache
        for node_uuid in node_uuid_list:
            if node_uuid in self._uuid_images:
                del self._uuid_images[node_uuid]

    @error_handle_odm
    # TODO: This is not a completely good function
    def create_relationships(self, rel_list):
        # Prepares arguments
        fail_list = []
        for i, item in enumerate(rel_list):
            if item['start_node_uuid'] not in self._uuid_images \
                    or item['end_node_uuid'] not in self._uuid_images:
                fail_list.append(i)
                continue

        # Removes the nodes with incorrect model names
        deleted_count = 0
        for i in fail_list:
            rel_list.pop(i - deleted_count)
            deleted_count += 1

        # All given uuids are bad
        if len(rel_list) == 0:
            return

        # Prepares MATCH statement
        match_str = 'MATCH '
        for i, item in enumerate(rel_list):
            match_str += '(a{0}:Node {{uuid: {1}}}), (b{0}:Node {{uuid: {2}}}), '\
                .format(i, json.dumps(item['start_node_uuid']),
                        json.dumps(item['end_node_uuid']))
        match_str = match_str[:len(match_str) - 2] + ' '

        # Prepares CREATE statement
        create_str = 'CREATE UNIQUE '
        for i, item in enumerate(rel_list):
            create_str += '(a{0})-[r{0}:`{1}` {2}]->(b{0}), '\
                .format(i, item['type'], self._str(item['params']))
        create_str = create_str[:len(create_str) - 2]

        # Builds query and runs it
        query_string = match_str + create_str
        self._run_query(query_string)

    @error_handle_odm
    def delete_relationships(self, rel_list):
        # Prepares MATCH statement
        match_str = 'MATCH '
        for i, item in enumerate(rel_list):
            match_str += '(a{0}:Node {{uuid: {1}}})' \
                         '-[r{0}]->(b{0}:Node {{uuid: {2}}}), '\
                .format(i, json.dumps(item['start_node_uuid']),
                        json.dumps(item['end_node_uuid']))
        match_str = match_str[:len(match_str) - 2] + ' '

        # Prepares DELETE statement
        delete_str = 'DELETE '
        for i in range(0, len(rel_list)):
            delete_str += '(r{0}), '.format(i)
        delete_str = delete_str[:len(delete_str) - 2]

        # Builds query and runs it
        query_string = match_str + delete_str
        self._run_query(query_string)

    @error_handle_odm
    def execute_query(self, query_string, query_params):
        return self._execute_query(query_string, **query_params)

    @error_handle_odm
    def run_query(self, query_string, query_params):
        self._run_query(query_string, **query_params)


class Connection():
    def __init__(self, client_id, conn, manager):
        self._id = client_id
        self._conn = conn
        self._manager = manager

    def _send(self, data):
        try:
            send_message(self._conn, data)
        except Exception, e:
            logger.log(info_level, 'Not sent data {data}'.format(data=data))
            logger.log(error_level, 'Sending data to client {id} failed. {error}'
                       .format(id=self._id, error=str(e)))

    def _recv(self, logs=True):
        data = None
        try:
            data = get_message(self._conn)
        except Exception, e:
            if logs:
                logger.log(
                    error_level,
                    'Receiving data from client {id} failed. '
                    '{error}'.format(id=self._id, error=str(e))
                )
        return data

    def _disconnect(self):
        try:
            self._conn.close()
            logger.log(info_level, 'Client {id} disconnected.'
                       .format(id=self._id))
        except Exception, e:
            logger.log(error_level, 'Disconnecting with client {id} failed. '
                                    '{error}'.format(id=self._id, error=str(e)))

    @error_handle_odm
    def _execute_function(self, request):
        func_name = request['func_name']
        args = request['args']

        if func_name != 'execute_query' and func_name != 'run_query':
            for i in range(0, len(args)):
                args[i] = [args[i]]

        logger.log(info_level, 'Client {id}: {func_name}'.format(
            id=self._id, func_name=func_name
        ))

        func = getattr(self._manager, str(func_name))

        results = func(*args)
        return results

    @error_handle_odm
    def _execute_batch(self, request):
        tasks = request['tasks']
        count = request['count']

        # Prepares request to be executed
        # TODO: consider execute_query and run_query as nonbatchable
        results = []
        for i in range(0, count):
            results.append([None])

        for func_name, params in tasks.iteritems():
            full_args = []
            for i in range(0, len(params[0][0])):
                full_args.append([])
            for args, no in params:
                for i, item in enumerate(args):
                    full_args[i].append(item)

            logger.log(info_level, 'Client {id}: {func_name}'.format(
                id=self._id, func_name=func_name
            ))

            func = getattr(self._manager, str(func_name))
            raw_results = func(*full_args)

            if raw_results:
                for i, item in enumerate(raw_results):
                    results[params[i][1]] = item

        return results

    def handle(self):
        while True:
            request = self._recv(logs=False)
            if not request:
                break

            try:
                # Single request or batch
                if 'tasks' not in request:
                    results = self._execute_function(request)
                else:
                    results = self._execute_batch(request)
                self._send(results)
            except:
                pass

        self._disconnect()


class ODMServer(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._manager = DatabaseManager()
        self._dynamic_id = 0

    def _get_new_id(self):
        self._dynamic_id += 1
        return self._dynamic_id

    def _handle_connections(self, server_socket):
        while True:
            conn, addr = server_socket.accept()
            new_id = self._get_new_id()
            conn = Connection(new_id, conn, self._manager)
            Thread(target=conn.handle).start()
            logger.log(info_level, 'Client {id} connected {addr}.'
                       .format(addr=addr, id=new_id))

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server_socket.bind((self._host, self._port))
            server_socket.listen(10)
            logger.log(info_level, 'The server is listening on port {port}.'
                       .format(port=self._port))
            self._handle_connections(server_socket)
        except Exception, e:
            logger.log(error_level, 'Starting server failed. {error}'
                       .format(error=str(e)))

if __name__ == '__main__':
    server = ODMServer(HOST, PORT)
    server.start()
