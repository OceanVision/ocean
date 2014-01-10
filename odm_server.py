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


class DatabaseManager:
    """ Driver for Neo4j database """

    def __init__(self):
        """Create DatabaseManager driver"""

        logger.log(info_level, "Created DatabaseManager object")

        self._graph_db = neo4j.GraphDatabaseService('http://localhost:7474/db/data/')
        self._uuid_images = dict()
        self._type_images = dict()

        self._init_uuid_images()
        self._init_types()

    def get_by_uuid(self, **params):
        try:
            node_uuid = params['node_uuid']

            if node_uuid not in self._uuid_images:
                return {}

            query_string = 'START e=node({node_id})\n' \
                           'RETURN e'
            cypher_query = neo4j.CypherQuery(self._graph_db, query_string)
            query_results = cypher_query.execute(node_id=self._uuid_images[node_uuid])

            if len(query_results) == 0:
                raise
            return query_results[0].values[0].get_properties()
        except Exception, e:
            logger.log(error_level, "Failed get_by_uuid "+str(e))
            return {}

    def get_by_link(self, **params):
        try:
            type = params['type']
            link = params['link']

            if type not in self._type_images:
                return {}

            type_id = self._uuid_images[self._type_images[type]]
            query_string = 'START e=node({type_id})\n' \
                           'MATCH (e)-[]->(a)\n' \
                           'WHERE a.link={link}\n' \
                           'RETURN a'
            cypher_query = neo4j.CypherQuery(self._graph_db, query_string)
            query_results = cypher_query.execute(type_id=type_id,
                                                 link=str(link))

            if len(query_results) == 0:
                return {}
            return query_results[0].values[0].get_properties()
        except:
            return {}

    def set(self, **params):
        try:
            node_uuid = params['node_uuid']
            node_params = params['node_params']

            if node_uuid not in self._uuid_images:
                return {}

            query_string = 'START e=node({node_id})\n' \
                           'SET {node_params}\n' \
                           'RETURN e'.format(node_id=self._uuid_images[node_uuid],
                                             node_params=self._str(node_params))
            # nie wiem jeszcze jak inaczej parametryzowac tutaj, to bardziej zlozona sprawa
            cypher_query = neo4j.CypherQuery(self._graph_db, query_string)
            query_results = cypher_query.execute()

            if len(query_results) == 0:
                raise
            return query_results[0].values[0].get_properties()
        except Exception as e:
            print e.message
            return {}

    def add_node(self, **params):
        try:
            type = params['type']
            node_params = params['node_params']

            if type not in self._type_images:
                return {}

            node_params['uuid'] = str(uuid.uuid1())
            query_string = 'CREATE e=({node_params})\n' \
                           'RETURN id(e), e'
            cypher_query = neo4j.CypherQuery(self._graph_db, query_string)
            node_results = cypher_query.execute(node_params=node_params)

            if len(node_results) == 0:
                raise

            self._uuid_images[node_params['uuid']] = node_results[0].values[0]
            rel_results = self.add_rel(start_node_uuid=self._type_images[type],
                                       end_node_uuid=node_params['uuid'],
                                       rel_type='<<INSTANCE>>')

            return {'node': node_results[0].values[1].get_properties(),
                    'rel': rel_results}
        except:
            return {}

    def delete_node(self, **params):
        try:
            node_uuid = params['node_uuid']

            if node_uuid not in self._uuid_images:
                return {}

            print self._uuid_images[node_uuid]
            query_string = 'START e=node({node_id})\n' \
                           'MATCH (e)-[r]-()\n' \
                           'DELETE e, r'
            cypher_query = neo4j.CypherQuery(self._graph_db, query_string)
            cypher_query.run(node_id=self._uuid_images[node_uuid])

            del self._uuid_images[node_uuid]
            return {}
        except:
            return {}

    def add_rel(self, **params):
        try:
            start_node_uuid = params['start_node_uuid']
            end_node_uuid = params['end_node_uuid']
            rel_type = params['rel_type']
            rel_params = params['rel_params'] if 'rel_params' in params else {}

            if start_node_uuid not in self._uuid_images or end_node_uuid not in self._uuid_images:
                return {}

            start_node_id = self._uuid_images[start_node_uuid]
            end_node_id = self._uuid_images[end_node_uuid]

            query_string = 'START a=node({start_node_id}), b=node({end_node_id})\n' \
                           'CREATE (a)-[r:`{rel_type}` {rel_params}]->(b)\n' \
                           'RETURN r'
            cypher_query = neo4j.CypherQuery(self._graph_db, query_string)
            query_results = cypher_query.execute(start_node_id=start_node_id,
                                                 end_node_id=end_node_id,
                                                 rel_type=str(rel_type),
                                                 rel_params=rel_params)

            if len(query_results) == 0:
                raise
            return query_results[0].values[0].get_properties()
        except Exception as e:
            return {}

    #def get_all_instances(self, **params):
    #    """
    #        Get all instances of given type
    #        @param
    #    """
    #
    #    try:
    #        query = \
    #        """
    #        START root=node(0)
    #        MATCH root-[r:`<<TYPE>>`]->typenode-[q:`<<INSTANCE>>`]->n
    #        WHERE typenode.model_name = { class_name }
    #        RETURN n
    #        """


    def delete_rel(self, **params):

        try:
            start_node_uuid = params['start_node_uuid']
            end_node_uuid = params['end_node_uuid']

            if start_node_uuid not in self._uuid_images or end_node_uuid not in self._uuid_images:
                return {}

            start_node_id = self._uuid_images[start_node_uuid]
            end_node_id = self._uuid_images[end_node_uuid]

            #TODO: this function should use get_query_results here, or fire_query for instance
            query_string = 'START a=node({start_node_id}), b=node({end_node_id})\n' \
                           'MATCH (a)-[r]-(b)\n' \
                           'DELETE r'
            cypher_query = neo4j.CypherQuery(self._graph_db, query_string)
            cypher_query.run(start_node_id=start_node_id,
                             end_node_id=end_node_id)

            return {}
        except:
            return {}

    def get_query_results(self, **params):
        try:
            query_string = params['query_string']
            query_params = params['query_params'] if 'query_params' in params else {}

            cypher_query = neo4j.CypherQuery(self._graph_db, str(query_string))
            query_results = cypher_query.execute(**query_params)

            results = []
            for result in query_results:
                results.append(result.values[0].get_properties())
            return results
        except:
            return []



    def _init_types(self):
        self._type_images.clear()
        #TODO: this function should use get_query_results here
        query = 'START e=node(0)\n' \
                'MATCH e-[]->t\n' \
                'RETURN t.uuid, t'
        cypher_query = neo4j.CypherQuery(self._graph_db, query)
        query_results = cypher_query.execute()
        for record in query_results:
            key = record.values[1]['model_name']
            value = record.values[0]
            self._type_images[key] = value

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
