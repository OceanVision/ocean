import sys
import os
import logging
import inspect
import socket

# The new Lionfish client (works properly only with the new server which is
# based on Scala).

sys.path.append(os.path.abspath(os.path.join(__file__, "../../../../")))

PORT, HOST = 0, ""

try:
    import don_corleone.don_utils as du
    HOST = du.get_configuration('lionfish', 'host')
    PORT = du.get_configuration('lionfish', 'port')
except Exception, e:
    print "FAILED TO FETCH HOST AND PORT CONFIGURATION FROM DON CORLEONE"
    print str(e)
    exit(1)

    
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../graph_workers'))
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

            method_name = data['methodName']
            if method_name not in self.tasks:
                self.tasks[method_name] = [[data['args'], self.count]]
            else:
                self.tasks[method_name].append([data['args'], self.count])
            self.count += 1

        def submit(self):
            """
            Executes tasks which are currently appended to the list
            """
            request = {
                'type': 'batch',
                'tasks': self.tasks,
                'count': self.count
            }

            self.client.send(request)
            results = self.client.recv()

            self.tasks = {}
            self.count = 0
            return results

    def __init__(self, host=HOST, port=PORT):
        self._host = host
        self._port = port
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self._conn.connect((self._host, self._port))
            logger.log(error_level, 'The client has connected to {host}:{port}.'
                       .format(host=self._host, port=self._port))
        except Exception as e:
            logger.log(error_level, 'Connecting failed. {error}'
                       .format(error=str(e)))
            raise e

    def disconnect(self):
        try:
            self._conn.close()
            logger.log(info_level, 'The client has disconnected.')
        except Exception as e:
            logger.log(error_level, 'Disconnecting failed. {error}'
                       .format(error=str(e)))
            raise e

    def send(self, data):
        try:
            send_message(self._conn, data)
        except Exception, e:
            logger.log(info_level, 'Not sent data {data}'.format(data=data))
            logger.log(error_level, 'Sending data failed. {error}'
                       .format(error=str(e)))
            raise e

    def recv(self):
        data = None
        try:
            data = get_message(self._conn)
        except Exception as e:
            logger.log(error_level, 'Receiving data failed. {error}'
                       .format(error=str(e)))
            raise e
        return data

    def get_batch(self):
        return self.Batch(self)

    def get_by_uuid(self, uuid, **params):
        """
        Gets a node of given uuid
        @param uuid string
        """
        data = {
            'methodName': 'getByUuid',
            'args': {
                'uuid': uuid
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        return self.recv()

    def get_by_link(self, model_name, link, **params):
        """
        Gets a node by given model_name and link
        @param model_name string
        @param link string
        """
        data = {
            'methodName': 'getByLink',
            'args': {
                'modelName': model_name,
                'link': link
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        return self.recv()

    def get_model_nodes(self, **params):
        """
        Gets model nodes
        """
        data = {
            'methodName': 'getModelNodes',
            'args': {}
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        return self.recv()

    def get_children(self, parent_uuid, relationship_type, children_properties, relationship_properties={},
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
            'methodName': 'getChildren',
            'args': {
                'parentUuid': parent_uuid,
                'relType': relationship_type,
                'childrenProps': children_properties,
                'relProps': relationship_properties
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        return self.recv()

    def get_instances(self, model_name, children_properties={}, relationship_properties={}, **params):
        """
        Gets all instances of given model_name with children_properties and relationship_properties
        @param model_name string
        @param children_properties dictionary
        @param relationship_properties dictionary
        """
        data = {
            'methodName': 'getInstances',
            'args': {
                'modelName': model_name,
                'childrenProps': children_properties,
                'relProps': relationship_properties
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        return self.recv()

    def set(self, uuid, **properties):
        """
        Sets properties to a node of given uuid
        @param uuid string
        @param properties dictionary/keywords
        """
        data = {
            'methodName': 'setProperties',
            'args': {
                'uuid': uuid,
                'props': properties
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        self.recv()

    def set_properties(self, uuid, **properties):
        """
        Sets properties to a node of given uuid
        @param uuid string
        @param properties dictionary/keywords
        """
        data = {
            'methodName': 'setProperties',
            'args': {
                'uuid': uuid,
                'props': properties
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        self.recv()

    def delete_properties(self, uuid, **property_keys):
        """
        Deletes property_keys of a node of given uuid
        @param uuid string
        @param property_keys dictionary/keywords
        """
        data = {
            'methodName': 'deleteProperties',
            'args': {
                'uuid': uuid,
                'propKeys': property_keys
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        self.recv()

    def create_node(self, model_name, relationship_type='<<INSTANCE>>', **properties):
        """
        Creates a node with properties to the model given by model_name
        @param model_name string
        @param relationship_type string
        @param properties dictionary/keywords
        """
        data = {
            'methodName': 'createNodes',
            'args': {
                'modelName': model_name,
                'relType': relationship_type,
                'props': properties
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        return self.recv()

    def delete_node(self, uuid, **params):
        """
        Deletes a node of given uuid
        @param uuid string
        """
        data = {
            'methodName': 'deleteNodes',
            'args': {
                'uuid': uuid
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
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
            'methodName': 'createRelationships',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid,
                'type': relationship_type,
                'props': properties
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        return self.recv()

    def delete_relationship(self, start_node_uuid, end_node_uuid, **params):
        """
        Deletes a relationship between nodes of start_node_uuid and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        """
        data = {
            'methodName': 'deleteRelationships',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
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
            'methodName': 'setRelationshipProperties',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid,
                'props': properties
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
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
            'methodName': 'deleteRelationshipProperties',
            'args': {
                'startNodeUuid': start_node_uuid,
                'endNodeUuid': end_node_uuid,
                'propKeys': prop_keys
            }
        }

        request = {
            'type': 'sequence',
            'tasks': [data]
        }

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(request)
        self.recv()

    # def execute_query(self, query_string, **params):
    #     """
    #     Executes query_string with given query_params
    #         and returns results as python dictionaries
    #     @param query_string string
    #     @param params dictionary/keywords
    #     """
    #     data = {
    #         'methodName': 'execute_query',
    #         'args': [query_string, params]
    #     }
    #
    #     request = {
    #         'type': 'sequence',
    #         'tasks': [data]
    #     }
    #
    #     if inspect.stack()[1][3] == '_get_data_for_batch':
    #         return data
    #     self.send(request)
    #     return self.recv()
    #
    # def run_query(self, query_string, **params):
    #     """
    #     Runs query_string with given query_params
    #     @param query_string string
    #     @param params dictionary/keywords
    #     """
    #     data = {
    #         'methodName': 'run_query',
    #         'args': [query_string, params]
    #     }
    #
    #     request = {
    #         'type': 'sequence',
    #         'tasks': [data]
    #     }
    #
    #     if inspect.stack()[1][3] == '_get_data_for_batch':
    #         return data
    #     self.send(request)
    #     self.recv()
