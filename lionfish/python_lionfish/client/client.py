import sys
import os
import logging
import inspect
import socket

# The new Lionfish client (works properly only with the new server which is
# based on Scala).

HOST = 'localhost'  # 'ocean-lionfish.no-ip.biz'
PORT = 21

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../graph_workers/graph_workers'))
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
                                           '../../../logs/odm_server.log'))
ch_file.setLevel(info_level)
logger.addHandler(ch_file)


class Client(object):
    class Batch(object):
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

            func_name = data['funcName']
            if func_name not in self.tasks:
                self.tasks[func_name] = [[data['args'], self.count]]
            else:
                self.tasks[func_name].append([data['args'], self.count])
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

            self.tasks = {}
            self.count = 0
            return results

    def __init__(self):
        self._host = HOST
        self._port = PORT
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self._conn.connect((self._host, self._port))
            logger.log(error_level, 'The client has connected to {host}:{port}.'
                       .format(host=self._host, port=self._port))
        except Exception as e:
            logger.log(error_level, 'Connecting failed. {error}'
                       .format(error=str(e)))

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

    def get_by_uuid(self, uuid, **params):
        """
        Gets a node of given uuid
        @param uuid string
        """
        data = {
            'funcName': 'getByUuid',
            'args': {
                'uuid': uuid
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def get_by_link(self, model_name, link, **params):
        """
        Gets a node by given model_name and link
        @param model_name string
        @param link string
        """
        data = {
            'funcName': 'getByLink',
            'args': {
                'modelName': model_name,
                'link': link
            }
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
            'funcName': 'getModelNodes',
            'args': {}
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def get_children(self, parent_uuid, relationship_type, children_properties, relationship_properties,
    **params):
        """
        Gets children of node with parent_uuid uuid related by relation relationship_type
        with children_properties and relationship_properties
        @param node_uuid string
        @param relationship_type string
        @param children_properties dictionary
        @param relationship_properties dictionary
        """
        data = {
            'funcName': 'getChildren',
            'args': {
                'parentUuid': parent_uuid,
                'relType': relationship_type,
                'childrenProps': children_properties,
                'relProps': relationship_properties
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def get_instances(self, model_name, children_properties, relationship_properties, **params):
        """
        Gets all instances of given model_name with children_properties and relationship_properties
        @param model_name string
        @param children_properties dictionary
        @param relationship_properties dictionary
        """
        data = {
            'funcName': 'getInstances',
            'args': {
                'modelName': model_name,
                'childrenProps': children_properties,
                'relProps': relationship_properties
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def set(self, uuid, **properties):
        """
        Sets properties to a node of given uuid
        @param uuid string
        @param properties dictionary/keywords
        """
        data = {
            'funcName': 'setProperties',
            'args': {
                'uuid': uuid,
                'props': properties
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def set_properties(self, uuid, **properties):
        """
        Sets properties to a node of given uuid
        @param uuid string
        @param properties dictionary/keywords
        """
        data = {
            'funcName': 'setProperties',
            'args': {
                'uuid': uuid,
                'props': properties
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def delete_properties(self, uuid, **property_keys):
        """
        Deletes property_keys of a node of given uuid
        @param uuid string
        @param property_keys dictionary/keywords
        """
        data = {
            'funcName': 'deleteProperties',
            'args': {
                'uuid': uuid,
                'propKeys': property_keys
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def create_node(self, model_name, relationship_type='<<INSTANCE>>', **properties):
        """
        Creates a node with properties to the model given by model_name
        @param model_name string
        @param relationship_type string
        @param properties dictionary/keywords
        """
        data = {
            'funcName': 'createNodes',
            'args': {
                'modelName': model_name,
                'relType': relationship_type,
                'props': properties
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def delete_node(self, uuid, **params):
        """
        Deletes a node of given uuid
        @param uuid string
        """
        data = {
            'funcName': 'deleteNodes',
            'args': {
                'uuid': uuid
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def create_relationship(self, start_node_uuid, end_node_uuid, relationship_type, **properties):
        """
        Creates a relationship relationship_type with properties
        between nodes of start_node_uuid and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        @param relationship_type string
        @param properties dictionary/keywords
        """
        data = {
            'funcName': 'createRelationships',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid,
                'type': relationship_type,
                'props': properties
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def delete_relationship(self, start_node_uuid, end_node_uuid, **params):
        """
        Deletes a relationship between nodes of start_node_uuid and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        """
        data = {
            'funcName': 'deleteRelationships',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def set_relationship_properties(self, start_node_uuid, end_node_uuid, **properties):
        """
        Sets properties to a relationship between two nodes given by start_node_uuid
        and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        @param properties dictionary/keywords
        """
        data = {
            'funcName': 'setRelationshipProperties',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid,
                'props': properties
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def delete_relationship_properties(self, start_node_uuid, end_node_uuid, **prop_keys):
        """
        Deletes properties of a relationship between two nodes given by start_node_uuid
        and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        @param property_keys dictionary/keywords
        """
        data = {
            'funcName': 'deleteRelationshipProperties',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid,
                'propKeys': prop_keys
            }
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    # def execute_query(self, query_string, **params):
    #     """
    #     Executes query_string with given query_params
    #         and returns results as python dictionaries
    #     @param query_string string
    #     @param params dictionary/keywords
    #     """
    #     data = {
    #         'funcName': 'execute_query',
    #         'args': [query_string, params]
    #     }
    #
    #     if inspect.stack()[1][3] == '_get_data_for_batch':
    #         return data
    #     self.send(data)
    #     return self.recv()
    #
    # def run_query(self, query_string, **params):
    #     """
    #     Runs query_string with given query_params
    #     @param query_string string
    #     @param params dictionary/keywords
    #     """
    #     data = {
    #         'funcName': 'run_query',
    #         'args': [query_string, params]
    #     }
    #
    #     if inspect.stack()[1][3] == '_get_data_for_batch':
    #         return data
    #     self.send(data)
    #     self.recv()
