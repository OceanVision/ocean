import socket
import json

HOST = 'localhost'
PORT = 7777


class ODMClient():
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
                    print 'Connecting failed.'
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
        @param node_uuid string
        """
        data = {'func_name': 'get_by_uuid', 'params': {
            'node_uuid': node_uuid
        }}
        self._send(data)
        return self._recv()

    def get_by_link(self, type, link):
        """
        @param type string
        @param link string
        """
        data = {'func_name': 'get_by_link', 'params': {
            'type': type,
            'link': link
        }}
        self._send(data)
        return self._recv()

    def set(self, node_uuid, node_params):
        """
        @param node_uuid string
        @param node_params dictionary
        """
        data = {'func_name': 'set', 'params': {
            'node_uuid': node_uuid,
            'node_params': node_params
        }}
        self._send(data)
        return self._recv()

    def add_node(self, type, node_params):
        """
        @param type string
        @param node_params dictionary
        """
        data = {'func_name': 'add_node', 'params': {
            'type': type,
            'node_params': node_params
        }}
        self._send(data)
        return self._recv()

    def delete_node(self, node_uuid):
        """
        @param node_uuid string
        """
        data = {'func_name': 'delete_node', 'params': {
            'node_uuid': node_uuid
        }}
        self._send(data)
        self._recv()

    def add_rel(self, start_node_uuid, end_node_uuid, rel_type, rel_params={}):
        """
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
        @param node_uuid string
        """
        data = {'func_name': 'delete_rel', 'params': {
            'start_node_uuid': start_node_uuid,
            'end_node_uuid': end_node_uuid
        }}
        self._send(data)
        self._recv()

    def get_query_results(self, query_string, **query_params):
        """
        @param query_string string
        @param query_params dictionary/keywords
        """
        data = {'func_name': 'get_query_results', 'params': {
            'query_string': query_string,
            'query_params': query_params
        }}
        self._send(data)
        return self._recv()

    def __getattr__(self, item):
        """ Generic function calling in case there is no explicitly defined function, but there is such function in ODMServer """
        try:
            return getattr(self, item)
        except:
            def generic_result(**params):
                data = {'func_name' : item, 'params':params}
                print data
                self._send(data)
                return self._recv()
            return generic_result

# if __name__ == "__main__":
    # client = Client()
    # client.connect()

    # print client.get_by_uuid('f902ddb0-7971-11e3-8e5f-2cd05ae1c39b')
    # uuid = client.get_by_link('Website', 'http://www.gry-online.pl/')['uuid']
    # print client.set(uuid, {'atrybut': 5, 'atrybut2': 'dupa'})
    # print client.get_by_uuid(uuid)
    # print client.add_node('NeoUser', {'username': 'lolek'})
    # client.delete_node('b9cfdbb0-79ef-11e3-851c-2cd05ae1c39b')
    # print client.add_rel('a8d435bc-79f5-11e3-86e4-2cd05ae1c39b',
    #                      'eb3cb198-79f7-11e3-bc35-2cd05ae1c39b', {'name': 'ziom', 'lalaq': 2})
    # print client.delete_rel('a8d435bc-79f5-11e3-86e4-2cd05ae1c39b', 'eb3cb198-79f7-11e3-bc35-2cd05ae1c39b')
    # query_string = 'START e=node(326)\n' \
    #                'MATCH e-[]-a-[]-b\n' \
    #                'RETURN b'
    # results = client.get_query_results(query_string)
    # for result in results:
    #     print result

    # client.disconnect()