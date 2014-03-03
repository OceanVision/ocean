import socket
import json
import inspect
import os,sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from ocean_don_corleone.utils import get_configuration
HOST = get_configuration("odm_address")
PORT = get_configuration("odm_port")

import struct
""" Utils for  prefix length TCP """
def socket_read_n(sock, n):
    """ Read exactly n bytes from the socket.
        Raise RuntimeError if the connection closed before
        n bytes were read.
    """
    buf = ''
    while n > 0:
        data = sock.recv(n)
        if data == '':
            raise RuntimeError('unexpected connection close')
        buf += data
        n -= len(data)
    return buf
def get_message_raw(sock):
    """
        Returns raw message (using length prefix framing)
    """
    len_buf = socket_read_n(sock, 4) # Read exactly n bytes
    msg_len = struct.unpack('>L', len_buf)[0]
    msg_buf = socket_read_n(sock,msg_len)
    return msg_buf
def send_message_raw(sock, msg ):
    """
        Sends raw message (using length prefix framing)
    """
    print "Sending "+msg
    packed_len = struct.pack('>L', len(msg)) # Number of bytes
    sock.sendall(packed_len + msg)
def send_message(sock, msg):
    """
        Sends message of class message_class (using length prefix framing)
    """
    s = json.dumps(msg)
    packed_len = struct.pack('>L', len(s)) # Number of bytes
    sock.sendall(packed_len + s)
def get_message(sock):
    """
        Returns object deserialized by JSON (using length prefix framing)
    """
    len_buf = socket_read_n(sock, 4) # Read exactly n bytes
    msg_len = struct.unpack('>L', len_buf)[0]
    msg_buf = socket_read_n(sock,msg_len)
    return json.loads(msg_buf)

class ODMClient:
    class Batch:
        def __init__(self, client):
            self.client = client
            self.tasks = []

        def _get_data_for_batch(self, func, args):
            return func(*args)

        def append(self, func, args):
            """
            Appends ODM task to the list
            @param func function
            @param args list
            """
            data = self._get_data_for_batch(func, args)
            self.tasks.append(data)

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
            send_message(self._conn, data)
            #self._conn.send(json.dumps(data))
        except Exception, e:
            print 'Not sent data', data
            print 'Sending data failed.', str(e)


    def recv(self):
        data = None
        try:
            data = get_message(self._conn)
            #received_data = str(self._conn.recv(8192))
            #
            #data = json.loads(received_data) if len(received_data) > 0 else {}
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

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
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

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def get_model_nodes(self):
        """
        Gets model nodes
        """
        data = {'func_name': 'get_model_nodes', 'params': {}}

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def get_children(self, node_uuid, rel_type, **params):
        """
        Gets children of node with parent_uuid uuid
            related by relation rel_name with parameters
        @param node_uuid string
        @param rel_type string
        @param params dictionary/keywords
        """
        data = {'func_name': 'get_children', 'params': {
            'node_uuid': node_uuid,
            'rel_type': rel_type,
            'children_params': params
        }}

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
        data = {'func_name': 'get_instances', 'params': {
            'model_name': model_name,
            'children_params': params
        }}

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
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

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        return self.recv()

    def add_node(self, model_name, node_params):
        """
        Adds a node with node_params to the model given by model_name
        (with the associated relationship of <<INSTANCE>>)
        @param type string
        @param node_params dictionary
        """
        data = {'func_name': 'add_node', 'params': {
            'model_name': model_name,
            'node_params': node_params
        }}

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
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

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
        self.send(data)
        self.recv()

    def add_rel(self, start_node_uuid, end_node_uuid, rel_type, **params):
        """
        Adds a relationship rel_type with rel_params
            between nodes of start_node_uuid and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        @param rel_type string
        @param params dictionary/keywords
        """
        data = {'func_name': 'add_rel', 'params': {
            'start_node_uuid': start_node_uuid,
            'end_node_uuid': end_node_uuid,
            'rel_type': rel_type,
            'rel_params': params
        }}

        if inspect.stack()[1][3] == '_get_data_for_batch':
            return data
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
        data = {'func_name': 'execute_query', 'params': {
            'query_string': query_string,
            'query_params': params
        }}

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
        data = {'func_name': 'run_query', 'params': {
            'query_string': query_string,
            'query_params': params
        }}

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
