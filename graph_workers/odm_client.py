import socket
import json

HOST = 'localhost'
PORT = 7777


class ODMClient:
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
        print 'The client has connected to {0}:{1}.'.format(str(self._host), str(self._port))

    def disconnect(self):
        try:
            self._conn.close()
        except Exception as e:
            print 'Disconnecting failed.', str(e)

        print 'The client has disconnected.'

    def _send(self, data):
        try:
            self._conn.send(json.dumps(data))
        except Exception as e:
            print 'Sending data failed.', str(e)

    def _recv(self):
        data = None
        try:
            received_data = str(self._conn.recv(8192))
            data = json.loads(received_data) if len(received_data) > 0 else {}
        except Exception as e:
            print 'Receiving data failed.', str(e)
        return data

    def get_by_uuid(self, node_uuid):
        """
        Gets a node of given node_uuid
        @param node_uuid string
        """
        data = {'func_name': 'get_by_uuid', 'params': {
            'node_uuid': node_uuid
        }}
        self._send(data)
        return self._recv()

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
        self._send(data)
        return self._recv()

    def get_all_instances(self, model_name):
        """
        Gets all instances of given model_name
        @param model_name string
        """
        data = {'func_name': 'get_all_instances', 'params': {
            'model_name': model_name
        }}
        self._send(data)
        return self._recv()

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
        self._send(data)
        return self._recv()

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
        self._send(data)
        return self._recv()

    def delete_node(self, node_uuid):
        """
        Deletes a node of given node_uuid
        @param node_uuid string
        """
        data = {'func_name': 'delete_node', 'params': {
            'node_uuid': node_uuid
        }}
        self._send(data)
        self._recv()

    def add_rel(self, start_node_uuid, end_node_uuid, rel_type, rel_params={}):
        """
        Adds a relationship rel_type with rel_params between nodes of start_node_uuid and end_node_uuid
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
        self._send(data)
        return self._recv()

    def delete_rel(self, start_node_uuid, end_node_uuid):
        """
        Deletes a relationship between nodes of start_node_uuid and end_node_uuid
        @param start_node_uuid string
        @param end_node_uuid string
        """
        data = {'func_name': 'delete_rel', 'params': {
            'start_node_uuid': start_node_uuid,
            'end_node_uuid': end_node_uuid
        }}
        self._send(data)
        self._recv()

    def get_query_results(self, query_string, **query_params):
        """
        Gets query_string results with given query_params
        @param query_string string
        @param query_params dictionary/keywords
        """
        data = {'func_name': 'get_query_results', 'params': {
            'query_string': query_string,
            'query_params': query_params
        }}
        self._send(data)
        return self._recv()

    def run_query(self, query_string, **query_params):
        """
        Executes query_string with given query_params
        @param query_string string
        @param query_params dictionary/keywords
        """
        data = {'func_name': 'run_query', 'params': {
            'query_string': query_string,
            'query_params': query_params
        }}
        self._send(data)
        self._recv()

    def __getattr__(self, item):
        """ Generic function calling in case there is no explicitly defined function """
        try:
            return getattr(self, item)
        except:
            def generic_result(**params):
                data = {'func_name': item, 'params': params}
                self._send(data)
                return self._recv()
            return generic_result

# if __name__ == "__main__":
    # client = ODMClient()
    # client.connect()

    # print client.get_by_uuid('e8eb82ae-7a45-11e3-9f04-2cd05ae1c39b')
    # print client.get_by_link('Website', 'http://www.gry-online.pl/')
    # print client.set(uuid, {'atrybut': 5, 'atrybut2': 'dupa'})
    # print client.get_by_uuid(uuid)
    # print client.add_node('NeoUser', {'username': 'ziom'})
    # client.delete_node('1783f6e8-7a49-11e3-84c1-2cd05ae1c39b')
    # print client.add_rel('1783f6e8-7a49-11e3-84c1-2cd05ae1c39b',
    #                      'e9174542-7a45-11e3-9f04-2cd05ae1c39b', {'name': 'ziomalska_relacja', 'lala': 2})
    # print client.delete_rel('a8d435bc-79f5-11e3-86e4-2cd05ae1c39b', 'eb3cb198-79f7-11e3-bc35-2cd05ae1c39b')
    # query_string = \
    #     '''
    #     START e=node(345)
    #     MATCH (e)-[]-(a)-[]-(b)
    #     RETURN b
    #     '''
    # results = client.get_query_results(query_string)
    # for result in results:
    #     print result

    # client.disconnect()