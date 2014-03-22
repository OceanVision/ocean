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
from threading import Thread
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'graph_workers'))
from graph_defines import *
from graph_utils import *

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
                                           'logs/odm_server.log'))
ch_file.setLevel(info_level)
logger.addHandler(ch_file)


class DatabaseManager(object):
    """ Driver for Neo4j database """
    def __init__(self):
        """ Creates DatabaseManager driver """
        logger.log(info_level, 'Created DatabaseManager object')
        self._graph_db = \
            neo4j.GraphDatabaseService('http://localhost:7474/db/data/')
        self._uuid_images = dict()
        self._model_name_images = dict()

        self._init_uuid_images()
        self._init_model_name_images()

    def _init_model_name_images(self):
        self._model_name_images.clear()
        query_string = \
            '''
            MATCH (e)-[]->(t)
            WHERE id(e) = 0
            RETURN t.uuid, (t)
            '''
        query_results = self._execute_query(query_string)
        for record in query_results:
            key = record[1]['model_name']
            value = record[0]
            self._model_name_images[key] = value

    def _init_uuid_images(self):
        self._uuid_images.clear()
        query_string = \
            '''
            MATCH (e)
            WHERE id(e) <> 0
            RETURN id(e), (e)
            '''
        query_results = self._execute_query(query_string)
        for record in query_results:
            key = record[1]['uuid']
            value = record[0]
            self._uuid_images[key] = value

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
        # Extracts ids from a list of uuids
        # TODO: this code assumes that all uuid->id mapping is in memory
        node_id_list = []
        for node_uuid in node_uuid_list:
            if str(node_uuid) not in self._uuid_images:
                raise Exception('Unknown uuid')
            node_id_list.append(self._uuid_images[node_uuid])

        # Builds query and gets results
        query_string = \
            '''
            MATCH (e)
            WHERE id(e) IN {node_id_list}
            RETURN (e)
            '''
        results = self._execute_query(query_string, node_id_list=node_id_list)
        return [item[0] for item in results]

    @error_handle_odm
    def get_by_link(self, node_list):
        # Extracts ids from a list of model names
        model_id_list = []
        for node in node_list:
            model_name = node['model_name']
            if model_name not in self._model_name_images:
                raise Exception('Unknown model name')
            node['model_id'] = \
                self._uuid_images[self._model_name_images[model_name]]

        # Prepares MATCH statement
        match_str = 'MATCH (e)-[r1:`<<TYPE>>`]->(t)-[r2:`<<INSTANCE>>`]->(a)\n'

        # Prepares WHERE clause
        where_str = 'WHERE id(e) = 0 AND HAS(a.link) AND ('
        for node in node_list:
            where_str += '(id(t) = {model_id} ' \
                         'AND a.link = {link}) OR '\
                .format(
                    model_id=node['model_id'],
                    link=json.dumps(node['link'], ensure_ascii=False)
                )
        where_str = where_str[:len(where_str) - 4] + ')\n'

        # Prepares RETURN statement
        return_str = 'RETURN (a)'

        # Builds query and gets results
        query_string = match_str + where_str + return_str
        results = self._execute_query(query_string)
        return [item[0] for item in results]

    @error_handle_odm
    def get_model_nodes(self):
        # Builds query and gets results
        query_string = \
            '''
            MATCH (e)-[r:`<<TYPE>>`]->(a)
            WHERE id(e) = 0
            RETURN (a)
            '''
        return self._execute_query(query_string)

    @error_handle_odm
    def get_children(self, node_list):
        # Extracts ids from a list of uuids
        for node in node_list:
            node_uuid = node['uuid']
            if node_uuid not in self._uuid_images:
                raise Exception('Unknown uuid')
            node['id'] = self._uuid_images[node_uuid]

        # Prepares MATCH statement
        match_str = 'MATCH (e)-[r]->(a)\n'

        # Prepares WHERE clause
        where_str = 'WHERE '
        for i, node in enumerate(node_list):
            if 'children_params' in node and len(node['children_params']) > 0:
                for key, value in node['children_params'].iteritems():
                    where_str += '(id(e) = {node_id} AND type(r) = {rel_type} ' \
                                 'AND a.{key} = {value}) OR '\
                        .format(
                            node_id=node['id'],
                            rel_type=unicode(
                                json.dumps(node['rel_type'], ensure_ascii=False)
                            ),
                            key=key,
                            value=unicode(json.dumps(value, ensure_ascii=False))
                        )
            else:
                where_str += '(id(e) = {node_id} AND type(r) = {rel_type}) OR '\
                    .format(
                        node_id=node['id'],
                        rel_type=unicode(
                            json.dumps(node['rel_type'], ensure_ascii=False)
                        )
                    )
        where_str = where_str[:len(where_str) - 4] + '\n'

        # Prepares RETURN statement
        return_str = 'RETURN (a), id(e)'

        # Builds query and gets results
        query_string = match_str + where_str + return_str

        # Extracts results from default lists
        raw_results = self._execute_query(query_string)
        results = []
        for i, node in enumerate(node_list):
            results.append([])
            for item in raw_results:
                if item[1] == node['id']:
                    results[i].append(item[0])

        return results

    @error_handle_odm
    def get_instances(self, model_name_list):
        # Prepares params for get_children
        node_list = []
        for model_name in model_name_list:
            node = {
                'uuid': self._model_name_images[model_name],
                'rel_type': '<<INSTANCE>>'
            }
            node_list.append(node)

        # Executes get_children and return its results
        return self.get_children(node_list)

    @error_handle_odm
    def set(self, node_list):
        # Extracts ids from a list of uuids
        for node in node_list:
            node_uuid = node['uuid']
            if node_uuid not in self._uuid_images:
                raise Exception('Unknown uuid')
            node['id'] = self._uuid_images[node_uuid]

        # Prepares MATCH statement
        match_str = 'MATCH '
        for i in range(0, len(node_list)):
            match_str += '(e{no}), '.format(no=i)
        match_str = match_str[:len(match_str) - 2] + '\n'

        # Prepares WHERE clause
        where_str = 'WHERE '
        for i, node in enumerate(node_list):
            where_str += 'id(e{no}) = {node_id} AND '.format(
                no=i, node_id=node['id']
            )
        where_str = where_str[:len(where_str) - 5] + '\n'

        # Prepares SET statement
        set_str = 'SET '
        for i, node in enumerate(node_list):
            for key, value in node['params'].iteritems():
                set_str += 'e{no}.{key} = {value}, '.format(
                    no=i,
                    key=key,
                    value=unicode(json.dumps(value, ensure_ascii=False))
                )
        set_str = set_str[:len(set_str) - 2]

        # Builds query and runs it
        query_string = match_str + where_str + set_str
        self._run_query(query_string)

    @error_handle_odm
    def create_nodes(self, node_list):
        # Prepares params
        for node in node_list:
            model_name = node['model_name']
            if model_name not in self._model_name_images:
                raise Exception('Unknown model name')
            # Default values loaded from graph_defines
            # (for instances loved for Content)
            params = dict(GRAPH_MODELS[model_name]) \
                if model_name in GRAPH_MODELS else {}
            params.update(node['params'])
            params['uuid'] = str(uuid.uuid1())
            node['params'] = params

        # Builds query and gets results
        query_string = \
            '''
            CREATE (e {node_list})
            RETURN id(e)
            '''
        node_results = self._execute_query(
            query_string,
            node_list=[n['params'] for n in node_list]
        )

        if len(node_results) == 0:
            raise Exception('Executing query failed')

        # Connects relations to newly created nodes
        node_uuid_list = []
        rel_list = []
        for i, node in enumerate(node_list):
            self._uuid_images[node['params']['uuid']] = node_results[i][0]
            node_uuid_list.append(node['params']['uuid'])

            rel = {
                'start_node_uuid': self._model_name_images[node['model_name']],
                'end_node_uuid': node['params']['uuid'],
                'type': '<<INSTANCE>>'
            }
            rel_list.append(rel)

        self.create_relationships(rel_list)
        return node_uuid_list

    @error_handle_odm
    def delete_nodes(self, node_uuid_list):
        # Extracts ids from a list of uuids
        node_id_list = []
        for node_uuid in node_uuid_list:
            if node_uuid not in self._uuid_images:
                raise Exception('Unknown uuid')
            node_id_list.append(self._uuid_images[node_uuid])

        # Builds query and runs it
        query_string = \
            '''
            MATCH (e)-[r]-()
            WHERE id(e) IN {node_id_list}
            DELETE (e), (r)
            '''
        self._run_query(query_string, node_id_list=node_id_list)

        # Removes uuids of deleted nodes from cache
        for node_uuid in node_uuid_list:
            del self._uuid_images[node_uuid]

    @error_handle_odm
    def create_relationships(self, rel_list):
        # Extracts ids from a list of uuids and prepares rel params dict
        rel_params_dict = {}
        for i, rel in enumerate(rel_list):
            start_node_uuid = rel['start_node_uuid']
            end_node_uuid = rel['end_node_uuid']

            if start_node_uuid not in self._uuid_images \
                    or end_node_uuid not in self._uuid_images:
                raise Exception('Unknown uuid')

            rel['start_node_id'] = self._uuid_images[start_node_uuid]
            rel['end_node_id'] = self._uuid_images[end_node_uuid]

            rel_params_dict['params{no}'.format(no=i)] = rel['params'] \
                if 'params' in rel else {}

        # Prepares MATCH statement
        match_str = 'MATCH '
        for i in range(0, len(rel_list)):
            match_str += '(a{no}), (b{no}), '.format(no=i)
        match_str = match_str[:len(match_str) - 2] + '\n'

        # Prepares WHERE clause
        where_str = 'WHERE '
        for i, rel in enumerate(rel_list):
            where_str += 'id(a{no}) = {start_node_id} ' \
                         'AND id(b{no}) = {end_node_id} AND '\
                .format(
                    no=i,
                    start_node_id=rel['start_node_id'],
                    end_node_id=rel['end_node_id']
                )
        where_str = where_str[:len(where_str) - 5] + '\n'

        # Prepares CREATE statements
        create_str = ''
        for i, rel in enumerate(rel_list):
            create_str += 'CREATE (a{no})-[r{no}:`{type}` {{params{no}}}]->(b{no})\n'\
                .format(no=i, type=rel['type'])

        # Builds query and runs it
        query_string = match_str + where_str + create_str
        self._run_query(query_string, **rel_params_dict)

    @error_handle_odm
    def delete_relationships(self, rel_list):
        # Extracts ids from a list of uuids and prepares rel params dict
        for i, rel in enumerate(rel_list):
            start_node_uuid = rel['start_node_uuid']
            end_node_uuid = rel['end_node_uuid']

            if start_node_uuid not in self._uuid_images \
                    or end_node_uuid not in self._uuid_images:
                raise Exception('Unknown uuid')

            rel['start_node_id'] = self._uuid_images[start_node_uuid]
            rel['end_node_id'] = self._uuid_images[end_node_uuid]

        # Prepares MATCH statement
        match_str = 'MATCH '
        for i in range(0, len(rel_list)):
            match_str += '(a{no})-[r{no}]->(b{no}), '.format(no=i)
        match_str = match_str[:len(match_str) - 2] + '\n'

        # Prepares WHERE clause
        where_str = 'WHERE '
        for i, rel in enumerate(rel_list):
            where_str += 'id(a{no}) = {start_node_id} ' \
                         'AND id(b{no}) = {end_node_id} AND '\
                .format(
                    no=i,
                    start_node_id=rel['start_node_id'],
                    end_node_id=rel['end_node_id']
                )
        where_str = where_str[:len(where_str) - 5] + '\n'

        # Prepares DELETE statement
        delete_str = 'DELETE '
        for i in range(0, len(rel_list)):
            delete_str += '(r{no}), '.format(no=i)
        delete_str = delete_str[:len(delete_str) - 2]

        # Builds query and runs it
        query_string = match_str + where_str + delete_str
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

    def _recv(self):
        data = None
        try:
            data = get_message(self._conn)
        except Exception, e:
            logger.log(error_level, 'Receiving data from client {id} failed. '
                                    '{error}'.format(id=self._id, error=str(e)))
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

            for i, item in enumerate(raw_results):
                results[params[i][1]] = item

        return results

    def handle(self):
        while True:
            request = self._recv()
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

HOST = ''
PORT = 7777

if __name__ == '__main__':
    server = ODMServer(HOST, PORT)
    server.start()
