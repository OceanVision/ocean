import sys
import os
import logging
import inspect

HOST = 'localhost'#'ocean-db.no-ip.biz'
PORT = 7777

sys.path.append(os.path.join(os.path.dirname(__file__), 'graph_workers'))
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
                                           '../logs/odm_server.log'))
ch_file.setLevel(info_level)
logger.addHandler(ch_file)


class ODMClient:
    class Batch:
        def __init__(self, client):
            self.client = client
            self.tasks = {}
            self.count = 0

        def _get_data_for_batch(self, func, args, params):
            return func(*args, **params)

        def append(self, func, *args, **params):
            """
            Appends ODM task to the list
            @param func function
            @param args list
            """
            data = self._get_data_for_batch(func, args, params)

            func_name = data['func_name']
            if func_name not in self.tasks:
                self.tasks[func_name] = [(data['args'], self.count)]
            else:
                self.tasks[func_name].append((data['args'], self.count))
            self.count += 1

        def submit(self):
            """
            Executes tasks which are currently appended to the list
            """
            request = {
                'tasks': self.tasks,
                'count': self.count
            }
            self.client.send(request)
            results = self.client.recv()
            # print request
            self.tasks = {}
            self.count = 0
            return results

    def __init__(self):
        self._host = HOST
        self._port = PORT
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        while True:
            try:
                self._conn.connect((self._host, self._port))
            except Exception as e:
                self._port += 1
                if self._port > 9999:
                    logger.log(error_level, 'Connecting failed. {error}'
                               .format(error=str(e)))
                    return
            else:
                break
        logger.log(error_level, 'The client has connected to {host}:{port}.'
                   .format(host=self._host, port=self._port))

    def disconnect(self):
        try:
            self._conn.close()
            logger.log(info_level, 'The client has disconnected.')
        except Exception as e:
            logger.log(error_level, 'Disconnecting failed. {error}'
                       .format(error=str(e)))

    def send(self, data):
        try:
            send_message(self._conn, data)
        except Exception, e:
            logger.log(info_level, 'Not sent data {data}'.format(data=data))
            logger.log(error_level, 'Sending data failed. {error}'
                       .format(error=str(e)))

    def recv(self):
        data = None
        try:
            data = get_message(self._conn)
        except Exception as e:
            logger.log(error_level, 'Receiving data failed. {error}'
                       .format(error=str(e)))
        return data

    def get_batch(self):
        return self.Batch(self)

    def get_by_uuid(self, node_uuid, **params):
        """
        Gets a node of given node_uuid
        @param node_uuid string
        """
        data = {
            'func_name': 'get_by_uuid',
            'args': [node_uuid]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        results = self.recv()
        return results[0] if len(results) > 0 else {}

    def get_by_link(self, model_name, link, **params):
        """
        Gets a node by given model_name and link
        @param type string
        @param link string
        """
        data = {
            'func_name': 'get_by_link',
            'args': [model_name, link]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def get_model_nodes(self, **params):
        """
        Gets model nodes
        """
        data = {
            'func_name': 'get_model_nodes',
            'args': []
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        results = self.recv()
        return [r[0] for r in results]

    def get_children(self, node_uuid, rel_type, **params):
        """
        Gets children of node with parent_uuid uuid
        related by relation rel_name with parameters
        @param node_uuid string
        @param rel_type string
        @param params dictionary/keywords
        """
        data = {
            'func_name': 'get_children',
            'args': [{
                'uuid': node_uuid,
                'rel_type': rel_type,
                'children_params': params
            }]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def get_instances(self, model_name, **params):
        """
        Gets all instances of given model_name
        @param model_name string
        @param params dictionary/keywords
        """
        data = {
            'func_name': 'get_instances',
            'args': [model_name]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def set(self, node_uuid, node_params, **params):
        """
        Sets node_params to a node of given node_uuid
        @param node_uuid string
        @param node_params dictionary
        """
        data = {
            'func_name': 'set',
            'args': [{
                'uuid': node_uuid,
                'params': node_params
            }]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def create_node(self, model_name, node_params, **params):
        """
        Creates a node with node_params to the model given by model_name
        (with the associated relationship of <<INSTANCE>>)
        @param type string
        @param node_params dictionary
        """
        data = {
            'func_name': 'create_nodes',
            'args': [{
                'model_name': model_name,
                'params': node_params
            }]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def delete_node(self, node_uuid, **params):
        """
        Deletes a node of given node_uuid
        @param node_uuid string
        """
        data = {
            'func_name': 'delete_nodes',
            'args': [node_uuid]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def create_relationship(self, start_node_uuid, end_node_uuid, rel_type, **params):
        """
        Creates a relationship rel_type with rel_params
        between nodes of start_node_uuid and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        @param rel_type string
        @param params dictionary/keywords
        """
        data = {
            'func_name': 'create_relationships',
            'args': [{
                'start_node_uuid': start_node_uuid,
                'end_node_uuid': end_node_uuid,
                'type': rel_type,
                'params': params
            }]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def delete_relationship(self, start_node_uuid, end_node_uuid, **params):
        """
        Deletes a relationship between nodes of start_node_uuid
            and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        """
        data = {
            'func_name': 'delete_relationships',
            'args': [{
                'start_node_uuid': start_node_uuid,
                'end_node_uuid': end_node_uuid
            }]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def execute_query(self, query_string, **params):
        """
        Executes query_string with given query_params
            and returns results as python dictionaries
        @param query_string string
        @param params dictionary/keywords
        """
        data = {
            'func_name': 'execute_query',
            'args': [query_string, params]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def run_query(self, query_string, **params):
        """
        Runs query_string with given query_params
        @param query_string string
        @param params dictionary/keywords
        """
        data = {
            'func_name': 'run_query',
            'args': [query_string, params]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def __getattr__(self, item):
        """
        Generic function calling in case there is no explicitly defined function
        """
        try:
            return getattr(self, item)
        except:
            def generic_result(**params):
                data = {'func_name': item, 'params': params}
                self.send(data)
                return self.recv()
            return generic_result

# if __name__ == '__main__':
#     cl = ODMClient()
#     cl.connect()
#     batch = cl.get_batch()
#     batch.append(cl.get_children, '970f6d5c-a07d-11e3-9f3a-2cd05ae1c39b', '<<INSTANCE>>', username='brunokam')
#     batch.append(cl.get_by_uuid, '970f6d5c-a07d-11e3-9f3a-2cd05ae1c39b') # NeoUser
#     batch.append(cl.get_children, '970f37f6-a07d-11e3-9f3a-2cd05ae1c39b', '<<INSTANCE>>', language='pl')
#     batch.append(cl.get_by_uuid, '974ee6b2-a07d-11e3-9f3a-2cd05ae1c39b') # kudkudak
#     print batch.submit()
#     print cl.get_by_uuid('970f6d5c-a07d-11e3-9f3a-2cd05ae1c39b')
#     cl.disconnect()