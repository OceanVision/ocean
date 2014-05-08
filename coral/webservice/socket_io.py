import socket
import struct
import json


class IO(object):
    @staticmethod
    def _read_from_socket(sock, n):
        """
        Read exactly n bytes from the socket.
        Raise RuntimeError if the connection closed before n bytes were read.
        """
        buf = ''
        while n > 0:
            data = sock.recv(n)
            if data == '':
                raise RuntimeError('unexpected connection close')
            buf += data
            n -= len(data)
        return buf

    @staticmethod
    def send(conn, msg):
        """
        Sends data to socket
        """
        s = json.dumps(msg)
        packed_len = struct.pack('>L', len(s))  # Number of bytes
        conn.sendall(packed_len + s)

    @staticmethod
    def receive(conn):
        """
        Retrieves data from socket and then returns
        """
        len_buf = IO._read_from_socket(conn, 4)  # Read exactly n bytes
        msg_len = struct.unpack('>L', len_buf)[0]
        msg_buf = IO._read_from_socket(conn, msg_len)
        return json.loads(msg_buf)
