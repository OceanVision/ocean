import socket
from socket_io import IO


class CoreConnector(object):
    def __init__(self):
        self._host = 'localhost'
        self._port = 7778
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._conn.connect((self._host, self._port))
        except Exception as e:
            print 'Failed to connect with Coral core. {error}'.format(error=str(e))

    def disconnect(self):
        try:
            self._conn.close()
        except Exception as e:
            print 'Failed to disconnect from Coral core. {error}'.format(error=str(e))

    def process_request(self, request):
        response = None
        try:
            IO.send(self._conn, request)
            response = IO.receive(self._conn)
        except Exception, e:
            print 'Failed to make a request. {error}'.format(error=str(e))
        return response
