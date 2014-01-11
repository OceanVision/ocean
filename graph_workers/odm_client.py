import socket
import json

HOST = 'localhost'
PORT = 7777


class ODMClient:
    class Batch:
        def __init__(self, client):
            self.client = client
            self.tasks = []

        def append(self, func_name, **params):
            """
            Appends ODM task to the list
            @param func_name string
            @param params dictionary/keywords
            """
            self.tasks.append({'func_name': func_name, 'params': params})

        def execute(self):
            """
            Executes tasks which are currently appended to the list
            """
            self.client.send(self.tasks)
            results = self.client.recv()
            del self.tasks[0:len(self.tasks)]
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
                    print 'Connecting failed.', str(e)
                    return
            else:
                break
        print 'The client has connected to {0}:{1}.' \
            .format(str(self._host), str(self._port))

    def disconnect(self):
        try:
            self._conn.close()
        except Exception as e:
            print 'Disconnecting failed.', str(e)

        print 'The client has disconnected.'

    def send(self, data):
        try:
            self._conn.send(json.dumps(data))
        except Exception as e:
            print 'Sending data failed.', str(e)

    def recv(self):
        data = None
        try:
            received_data = str(self._conn.recv(8192))
            data = json.loads(received_data) if len(received_data) > 0 else {}
        except Exception as e:
            print 'Receiving data failed.', str(e)
        return data

    def get_batch(self):
        return self.Batch(self)

    def get_by_uuid(self, node_uuid):
        """
        Gets a node of given node_uuid
        @param node_uuid string
        """
        data = {'func_name': 'get_by_uuid', 'params': {
            'node_uuid': node_uuid
        }}
        self.send(data)
        return self.recv()

    def get_by_link(self, model_name, link):
        """
        Gets a node by given model_name and link
        @param type string
        @param link string
        """
        data = {'func_name': 'get_by_link', 'params': {
            'model_name': model_name,
            'link': link
        }}
        self.send(data)
        return self.recv()

    def get_model_nodes(self):
        """
        Gets model nodes
        """
        data = {'func_name': 'get_model_nodes', 'params': {}}
        self.send(data)
        return self.recv()

    def get_children(self, node_uuid, rel_type, **children_params):
        """
        Gets children of node with parent_uuid uuid
            related by relation rel_name with parameters
        @param node_uuid string
        @param rel_type string
        @param children_params dictionary/keywords
        """
        data = {'func_name': 'get_children', 'params': {
            'node_uuid': node_uuid,
            'rel_type': rel_type,
            'children_params': children_params
        }}
        print data
        self.send(data)
        return self.recv()

    def get_instances(self, model_name, **children_params):
        """
        Gets all instances of given model_name
        @param model_name string
        @param children_params dictionary/keywords
        """
        print 'ok'
        data = {'func_name': 'get_instances', 'params': {
            'model_name': model_name,
            'children_params': children_params
        }}
        self.send(data)
        return self.recv()

    def set(self, node_uuid, node_params):
        """
        Sets node_params to a node of given node_uuid
        @param node_uuid string
        @param node_params dictionary
        """
        data = {'func_name': 'set', 'params': {
            'node_uuid': node_uuid,
            'node_params': node_params
        }}
        self.send(data)
        return self.recv()

    def add_node(self, model_name, node_params):
        """
        Adds a node with node_params to the model given by model_name
        @param type string
        @param node_params dictionary
        """
        data = {'func_name': 'add_node', 'params': {
            'model_name': model_name,
            'node_params': node_params
        }}
        self.send(data)
        return self.recv()

    def delete_node(self, node_uuid):
        """
        Deletes a node of given node_uuid
        @param node_uuid string
        """
        data = {'func_name': 'delete_node', 'params': {
            'node_uuid': node_uuid
        }}
        self.send(data)
        self.recv()

    def add_rel(self, start_node_uuid, end_node_uuid, rel_type, rel_params={}):
        """
        Adds a relationship rel_type with rel_params
            between nodes of start_node_uuid and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        @param rel_type string
        @param rel_params dictionary
        """
        data = {'func_name': 'add_rel', 'params': {
            'start_node_uuid': start_node_uuid,
            'end_node_uuid': end_node_uuid,
            'rel_type': rel_type,
            'rel_params': rel_params
        }}
        self.send(data)
        return self.recv()

    def delete_rel(self, start_node_uuid, end_node_uuid):
        """
        Deletes a relationship between nodes of start_node_uuid
            and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        """
        data = {'func_name': 'delete_rel', 'params': {
            'start_node_uuid': start_node_uuid,
            'end_node_uuid': end_node_uuid
        }}
        self.send(data)
        self.recv()

    def execute_query(self, query_string, **query_params):
        """
        Executes query_string with given query_params
            and returns results as python dictionaries
        @param query_string string
        @param query_params dictionary/keywords
        """
        data = {'func_name': 'execute_query', 'params': {
            'query_string': query_string,
            'query_params': query_params
        }}
        self.send(data)
        return self.recv()

    def run_query(self, query_string, **query_params):
        """
        Runs query_string with given query_params
        @param query_string string
        @param query_params dictionary/keywords
        """
        data = {'func_name': 'run_query', 'params': {
            'query_string': query_string,
            'query_params': query_params
        }}
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