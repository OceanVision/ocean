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
logger = logging.getLogger(__name__ + "_ocean")
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),"logs/odm_server.log"), )
ch_file.setLevel(info_level)
logger.addHandler(ch_file)


#TODO: move to utils
def error_handle_odm(func):
    """ This decorator will return response to message.html with error if catched """
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
        self._graph_db = neo4j.GraphDatabaseService('http://localhost:7474/db/data/')
        self._uuid_images = dict()
        self._model_name_images = dict()

        self._init_uuid_images()
        self._init_types()

    def _init_types(self):
        self._model_name_images.clear()
        #TODO: this function should use get_query_results here
        query = 'START e=node(0)\n' \
                'MATCH e-[]->t\n' \
                'RETURN t.uuid, t'
        cypher_query = neo4j.CypherQuery(self._graph_db, query)
        query_results = cypher_query.execute()
        for record in query_results:
            key = record.values[1]['model_name']
            value = record.values[0]
            self._model_name_images[key] = value

    def _init_uuid_images(self):
        self._uuid_images.clear()
        query = 'START e=node(*)\n' \
                'WHERE id(e) <> 0\n' \
                'RETURN id(e), e'
        cypher_query = neo4j.CypherQuery(self._graph_db, query)
        query_results = cypher_query.execute()
        for record in query_results:
            key = record.values[1]['uuid']
            value = record.values[0]
            self._uuid_images[key] = value

    def _str(self, dictionary, element='e'):
        string = ''
        for (key, value) in dictionary.iteritems():
            if isinstance(value, basestring):
                string += ',' + str(element) + '.' + str(key) + '=' + '"' + str(value) + '"'
            else:
                string += ',' + str(element) + '.' + str(key) + '=' + str(value)
        return str(string[1:])

    @error_handle_odm
    def get_query_results(self, query_string, **query_params):
        """
        Executes query and returns results as python dictionaries
        @param query_string
        @param query_params
        """
        cypher_query = neo4j.CypherQuery(self._graph_db, str(query_string))
        query_results = cypher_query.execute(**query_params)

        results = []
        for result in query_results:
            values = []
            for value in result.values:
                if value.__class__.__name__ == 'Node' or value.__class__.__name__ == 'Relationship':
                    values.append(value.get_properties())
                else:
                    values.append(value)
            results.append(values)
        return results

    @error_handle_odm
    def run_query(self, query_string, **query_params):
        """
        Executes query only
        @param query_string
        @param query_params
        """
        cypher_query = neo4j.CypherQuery(self._graph_db, str(query_string))
        cypher_query.run(**query_params)

    @error_handle_odm
    def get_by_uuid(self, **params):
        node_uuid = params['node_uuid']

        if node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        query_string = \
            '''
            START e=node({node_id})
            RETURN e
            '''
        return self.get_query_results(query_string,
                                      node_id=self._uuid_images[params['node_uuid']])[0][0]

    @error_handle_odm
    def get_by_link(self, **params):
        model_name = params['model_name']
        link = params['link']

        if model_name not in self._model_name_images:
            raise Exception('Unknown type')

        query_string = \
            '''
            START e=node({model_name_id})
            MATCH (e)-[]->(a)
            WHERE a.link={link}
            RETURN a
            '''
        return self.get_query_results(query_string,
                                      model_name_id=self._uuid_images[self._model_name_images[model_name]],
                                      link=link)[0][0]

    @error_handle_odm
    def get_all_instances(self, **params):
        query_string = \
            '''
            START e=node(0)
            MATCH e-[r:`<<TYPE>>`]->t-[q:`<<INSTANCE>>`]->n
            WHERE t.model_name = {model_name}
            RETURN n
            '''
        return self.get_query_results(query_string,
                                      params)

    @error_handle_odm
    def set(self, **params):
        node_uuid = params['node_uuid']
        node_params = params['node_params']

        if node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        query_string = \
            '''
            START e=node({node_id})
            SET {node_params}
            RETURN e
            '''.format(node_id=self._uuid_images[node_uuid],
                       node_params=self._str(node_params))
        return self.get_query_results(query_string)[0][0]

    @error_handle_odm
    def add_node(self, **params):
        model_name = params['model_name']
        node_params = params['node_params']

        if model_name not in self._model_name_images:
            raise Exception('Unknown type')

        node_params['uuid'] = str(uuid.uuid1())
        query_string = \
            '''
            CREATE e=({node_params})
            RETURN id(e), e
            '''
        node_results = self.get_query_results(query_string, node_params=node_params)

        if len(node_results) == 0:
            raise Exception('Executing query failed')

        self._uuid_images[node_params['uuid']] = node_results[0][0]
        rel_results = self.add_rel(start_node_uuid=self._model_name_images[model_name],
                                   end_node_uuid=node_params['uuid'],
                                   rel_type='<<INSTANCE>>')
        return {'node': node_results[0][1],
                'rel': rel_results}

    @error_handle_odm
    def delete_node(self, **params):
        node_uuid = params['node_uuid']

        if node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        query_string = \
            '''
            START e=node({node_id})
            MATCH (e)-[r]-()
            DELETE e, r
            '''
        self.run_query(query_string,
                       node_id=self._uuid_images[node_uuid])
        del self._uuid_images[node_uuid]

    @error_handle_odm
    def add_rel(self, **params):
        start_node_uuid = params['start_node_uuid']
        end_node_uuid = params['end_node_uuid']
        rel_type = params['rel_type']
        rel_params = params['rel_params'] if 'rel_params' in params else {}

        if start_node_uuid not in self._uuid_images or end_node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid')

        start_node_id = self._uuid_images[start_node_uuid]
        end_node_id = self._uuid_images[end_node_uuid]

        query_string = \
            '''
            START a=node({start_node_id}), b=node({end_node_id})
            CREATE (a)-[r:`{rel_type}` {rel_params}]->(b)
            RETURN r
            '''
        query_results = self.get_query_results(query_string,
                                               start_node_id=start_node_id,
                                               end_node_id=end_node_id,
                                               rel_type=str(rel_type),
                                               rel_params=rel_params)
        if len(query_results) == 0:
            raise Exception('Executing query failed')
        return query_results[0][0]

    @error_handle_odm
    def delete_rel(self, **params):
        start_node_uuid = params['start_node_uuid']
        end_node_uuid = params['end_node_uuid']

        if start_node_uuid not in self._uuid_images or end_node_uuid not in self._uuid_images:
            raise Exception('Unknown uuid.')

        start_node_id = self._uuid_images[start_node_uuid]
        end_node_id = self._uuid_images[end_node_uuid]

        query_string = \
            '''
            START a=node({start_node_id}), b=node({end_node_id})
            MATCH (a)-[r]-(b)
            DELETE r
            '''
        self.run_query(query_string,
                       start_node_id=start_node_id,
                       end_node_id=end_node_id)


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
            print 'New connection from {0}, new client id: {1}'.format(str(addr), str(conn.id))

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
