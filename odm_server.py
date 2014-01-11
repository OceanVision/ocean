from py2neo import neo4j
import uuid
import os
import socket
from threading import Thread, Lock
import json
# Logging (TODO: move creation of logger to utils)
import logging

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


#TODO: move to utils
def error_handle_odm(func):
    """
    This decorator will return response to message.html with error if caught
    """
    def f(request, *args, **dict_args):
        try:
            return func(request, *args, **dict_args)
        except Exception, e:
            print '{0} failed with {1}.'.format(func.__name__, e)
            return {}
        except:
            print '{0} failed with not registered error.'.format(func.__name__)
            return {}

    f.__name__ = func.__name__
    return f


class DatabaseManager:
    """ Driver for Neo4j database """
    def __init__(self):
        """Create DatabaseManager driver"""
        logger.log(info_level, 'Created DatabaseManager object')
        self._graph_db = \
            neo4j.GraphDatabaseService('http://localhost:7474/db/data/')
        self._uuid_images = dict()
        self._model_name_images = dict()

        self._init_uuid_images()
        self._init_types()

    @error_handle_odm
    def _execute_query(self, query_string, multi_value=False, **query_params):
        """
        Executes query and returns results as python dictionaries
        @param query_string string
        @param multi_value bool
        @param query_params dictionary
        """
        cypher_query = neo4j.CypherQuery(self._graph_db, str(query_string))
        query_results = cypher_query.execute(**query_params)

        results = []
        for result in query_results:
            values = []
            if not multi_value:
                value = result.values[0]
                if value.__class__.__name__ in ('Node', 'Relationship'):
                    values = value.get_properties()
                else:
                    values = value
            else:
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
        cypher_query = neo4j.CypherQuery(self._graph_db, str(query_string))
        cypher_query.run(**query_params)

    def _init_types(self):
        self._model_name_images.clear()
        query_string = \
            '''
            START e=node(0)
            MATCH (e)-[]->(t)
            RETURN t.uuid, t
            '''
        query_results = self._execute_query(query_string, True)
        for record in query_results:
            key = record[1]['model_name']
            value = record[0]
            self._model_name_images[key] = value

    def _init_uuid_images(self):
        self._uuid_images.clear()
        query_string = \
            '''
            START e=node(*)
            WHERE id(e) <> 0
            RETURN id(e), e
            '''
        query_results = self._execute_query(query_string, True)
        for record in query_results:
            key = record[1]['uuid']
            value = record[0]
            self._uuid_images[key] = value

    def _str(self, dictionary, element='e', separator=','):
        string = ''
        for (key, value) in dictionary.iteritems():
            string += str(separator) + ' ' + str(element) + '.' \
                      + str(key) + '=' + json.dumps(value) + ' '
        return str(string[(len(separator) + 1):])

    @error_handle_odm
    def get_by_uuid(self, **params):
        node_uuid = params['node_uuid']

        #TODO: this code assumes that all uuid->id mapping is in memory,
        # it is not a good assumption
        # it should execute a query if asked for non exisiting uuid
        if node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        node_id = self._uuid_images[params['node_uuid']]
        query_string = \
            '''
            START e=node({node_id})
            RETURN e
            '''
        return self._execute_query(query_string, node_id=node_id)[0]

    @error_handle_odm
    def get_by_link(self, **params):
        model_name = params['model_name']

        if model_name not in self._model_name_images:
            raise Exception('Unknown type')

        mode_name_id = self._uuid_images[self._model_name_images[model_name]]
        link = params['link']
        query_string = \
            '''
            START e=node({model_name_id})
            MATCH (e)-[]->(a)
            WHERE a.link={link}
            RETURN a
            '''
        return self._execute_query(query_string, model_name_id=mode_name_id,
                                   link=link)[0]

    @error_handle_odm
    def get_type_nodes(self):
        """ Get type nodes """
        cypher_query = \
            '''
            START e=node(0)
            MATCH (e)-[r:`<<TYPE>>`]->(a)
            RETURN a
            '''
        return self._execute_query(cypher_query)

    @error_handle_odm
    def get_all_children(self, **params):
        node_uuid = params['node_uuid']

        if node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        node_id = self._uuid_images[node_uuid]
        children_params = params['children_params'] \
            if 'children_params' in params else {}
        rel_type = params['rel_type']
        cypher_query = \
            '''
            START e=node({node_id})
            MATCH (e)-[r:`''' + rel_type + '''`]->(a)
            ''' \
            + (('WHERE ' + self._str(children_params, 'a', 'AND')) \
            if len(children_params) > 0 else '') + \
            '''
            RETURN a
            '''
        # There is a problem with node_params if they are given to _run_query
        return self._execute_query(cypher_query, node_id=node_id)

    @error_handle_odm
    def get_all_instances(self, **params):
        """
        Gets all instances of given model_name
        @param model_name string
        """
        query_string = \
            '''
            START e=node(0)
            MATCH (e)-[r:`<<TYPE>>`]->(t)-[q:`<<INSTANCE>>`]->(n)
            WHERE t.model_name = {model_name}
            RETURN n
            '''
        return self._execute_query(query_string, **params)

    @error_handle_odm
    def set(self, **params):
        node_uuid = params['node_uuid']

        if node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        node_id = self._uuid_images[node_uuid]
        node_params = self._str(params['node_params'])
        query_string = \
            '''
            START e=node({node_id})
            SET {node_params}
            '''.format(node_id=node_id, node_params=node_params)
        # There is a problem with node_params if they are given to _run_query
        self._run_query(query_string)

    @error_handle_odm
    def add_node(self, **params):
        model_name = params['model_name']

        if model_name not in self._model_name_images:
            raise Exception('Unknown type')

        node_params = params['node_params']
        node_params['uuid'] = str(uuid.uuid1())
        query_string = \
            '''
            CREATE e=({node_params})
            RETURN id(e)
            '''
        node_results = self._execute_query(query_string,
                                           node_params=node_params)

        if len(node_results) == 0:
            raise Exception('Executing query failed')

        self._uuid_images[node_params['uuid']] = node_results[0]

        start_node_uuid = self._model_name_images[model_name]
        end_node_uuid = node_params['uuid']
        rel_type = '<<INSTANCE>>'
        self.add_rel(start_node_uuid=start_node_uuid,
                     end_node_uuid=end_node_uuid, rel_type=rel_type)
        return {'uuid': node_params['uuid']}

    @error_handle_odm
    def delete_node(self, **params):
        node_uuid = params['node_uuid']

        if node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        node_id = self._uuid_images[node_uuid]
        query_string = \
            '''
            START e=node({node_id})
            MATCH (e)-[r]-()
            DELETE e, r
            '''
        self._run_query(query_string, node_id=node_id)
        del self._uuid_images[node_uuid]

    @error_handle_odm
    def add_rel(self, **params):
        start_node_uuid = params['start_node_uuid']
        end_node_uuid = params['end_node_uuid']

        if start_node_uuid not in self._uuid_images \
            or end_node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        start_node_id = self._uuid_images[start_node_uuid]
        end_node_id = self._uuid_images[end_node_uuid]
        rel_type = params['rel_type']
        rel_params = params['rel_params'] if 'rel_params' in params else {}

        query_string = \
            '''
            START a=node({start_node_id}), b=node({end_node_id})
            CREATE (a)-[r:`''' + rel_type + '''` {rel_params}]->(b)
            '''
        # There is a problem with node_params if they are given to _run_query
        self._run_query(query_string, start_node_id=start_node_id,
                        end_node_id=end_node_id, rel_params=rel_params)

    @error_handle_odm
    def delete_rel(self, **params):
        start_node_uuid = params['start_node_uuid']
        end_node_uuid = params['end_node_uuid']

        if start_node_uuid not in self._uuid_images \
            or end_node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        start_node_id = self._uuid_images[start_node_uuid]
        end_node_id = self._uuid_images[end_node_uuid]

        query_string = \
            '''
            START a=node({start_node_id}), b=node({end_node_id})
            MATCH (a)-[r]->(b)
            DELETE r
            '''
        self._run_query(query_string, start_node_id=start_node_id,
                        end_node_id=end_node_id)

    @error_handle_odm
    def execute_query(self, **params):
        query_string = params['query_string']
        query_params = params['query_params']

        return self._execute_query(query_string, True, **query_params)

    @error_handle_odm
    def run_query(self, **params):
        query_string = params['query_string']
        query_params = params['query_params']

        self._run_query(query_string, **query_params)


class Connection():
    def __init__(self, client_id, conn):
        self.id = client_id
        self.conn = conn

    def send(self, data):
        try:
            self.conn.send(json.dumps(data))
        except Exception as e:
            print 'Sending data to client', self.id, 'failed.', e.message

    def recv(self):
        data = None
        try:
            received_data = str(self.conn.recv(8192))
            data = json.loads(received_data) if len(received_data) > 0 else {}
        except Exception as e:
            print 'Receiving data from client', self.id, 'failed.', e.message
        return data

    def disconnect(self):
        try:
            self.conn.close()
        except Exception as e:
            print 'Disconnecting with client', self.id, 'failed.', e.message


class ODMServer():
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._manager = DatabaseManager()
        self._dynamic_id = 0
        self._conn_list = []

    def _get_new_id(self):
        self._dynamic_id += 1
        return self._dynamic_id

    def _handle_client(self, conn, lock):
        while True:
            request = conn.recv()
            if not request:
                break

            try:
                func = getattr(self._manager, str(request['func_name']))
                print 'Client {0}: {1}'.format(conn.id, request['func_name'])
                results = func(**request['params'])
                conn.send(results)
            except:
                pass

        lock.acquire()
        self._conn_list.remove(conn)
        conn.disconnect()
        print 'Client {0} disconnected.'.format(str(conn.id))
        lock.release()

    def _handle_connections(self, server_socket, lock):
        while True:
            conn, addr = server_socket.accept()
            conn = Connection(self._get_new_id(), conn)
            self._conn_list.append(conn)
            Thread(target=self._handle_client, args=(conn, lock)).start()
            print 'New connection from {0}, new client id: {1}' \
                .format(str(addr), str(conn.id))

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                server_socket.bind((self._host, self._port))
            except socket.error:
                self._port += 1
                if self._port > 9999:
                    print 'Starting server failed.'
                    return
            else:
                break

        server_socket.listen(10)
        print 'The server is listening on port {0}.'.format(str(self._port))
        lock = Lock()
        self._handle_connections(server_socket, lock)

HOST = 'localhost'
PORT = 7777

if __name__ == '__main__':
    server = ODMServer(HOST, PORT)
    server.start()