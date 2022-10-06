"""
 Simple JSON-RPC Server

"""

import json
import socket
import functions


class JSONRPCServer:
    """The JSON-RPC server."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.funcs = {}

    def register(self, name, function):
        """Registers a function."""
        self.funcs[name] = function

    def start(self):
        """Starts the server."""
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print('Listening on port %s ...' % self.port)

        try:
            while True:
                # Accepts and handles client
                conn, _ = self.sock.accept()
                self.handle_client(conn)

                # Close client connection
                conn.close()

        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def stop(self):
        """Stops the server."""
        self.sock.close()

    def handle_client(self, conn):
        """Handles the client connection."""

        # Collection of errors
        errors = {
            '-32601': {'code': -32601, 'message': 'Method not found'},
            '-32602': {'code': -32602, 'message': 'Invalid params'},
            '-32600': {'code': -32600, 'message': 'Invalid Request'},
            '-32700': {'code': -32700, 'message': 'Parse error'}
        }

        # Receive message
        msg = conn.recv(1024).decode()
        print('Received:', msg)

        # Prepare response

        # Default response
        res = {
            'jsonrpc': '2.0',
            'id': 'No ID'
        }
        try:
            msg = json.loads(msg)
            method = msg['method']

            try:
                params = msg['params']
            except KeyError:
                params = ''

            if 'id' not in msg:
                res = ''
                return

            res['id'] = msg['id']

            try:
                func = self.funcs[method]
                res['result'] = func(*params)
            except KeyError:
                res['error'] = errors['-32601']
            except TypeError:
                res['error'] = errors['-32602']

        except KeyError:
            res['error'] = errors['-32600']
        except json.decoder.JSONDecodeError:
            res['error'] = errors['-32700']

        # Send response
        res = json.dumps(res)
        conn.send(res.encode())


if __name__ == "__main__":
    # Test the JSONRPCServer class
    server = JSONRPCServer('0.0.0.0', 8000)

    # Register functions
    server.register('hello', functions.hello)
    server.register('greet', functions.greet)
    server.register('add', functions.add)
    server.register('sub', functions.sub)
    server.register('mul', functions.mul)
    server.register('div', functions.div)

    # Start the server
    server.start()
