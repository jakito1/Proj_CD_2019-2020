"""
 Simple multi-threaded HTTP Server
"""

import socket
import threading
import json


def get_filename(temp):
    """Returns filename"""
    try:
        # Parse headers
        headers = temp.split('\n')
        get_content = headers[0].split()
        return get_content[1]
    except IndexError:
        return None


def get_close(temp):
    """Returns if it is to close connection"""
    try:
        # Parse headers
        headers = temp.split('\n')
        if 'close' in headers[1]:
            return True
        return False
    except IndexError:
        return False


def handle_post(temp):
    """Funtion to handle the post"""
    headers = temp.split('\n')
    get_content = headers[0].split()
    temp_list2 = []
    temp_dict = {}
    if get_content[0] == 'POST' and get_content[1] == '/form':
        temp_list1 = headers[8].split('&')
        if len(temp_list1) == 1:
            return 400
        for i in temp_list1:
            temp_list3 = i.split('=')
            temp_list2.append(temp_list3[0])
            temp_list2.append(temp_list3[1])
        for i in range(0, len(temp_list2), 2):
            temp_dict[temp_list2[i]] = temp_list2[i + 1]
        json_list = json.dumps(temp_dict)
        return json_list
    return headers[8]


def handle_request(temp_request):
    """Returns file content for client request"""
    headers = temp_request.split('\n')
    filename = get_filename(temp_request)
    try:
        temp_post = handle_post(temp_request)
        if (filename in ('/form', '/json')) and 'POST' in headers[0]:
            return temp_post
    except IndexError:
        pass

    # Check if forbidden
    try:
        if filename.startswith('/private/') or '/../' in filename or filename.startswith('/form'):
            return 403
    except AttributeError:
        return 400

    # Get filename
    try:
        if filename == '/':
            filename = '/index.html'
    except AttributeError:
        pass

    try:
        # Return file contents
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.mp3') \
                or filename.endswith('.mp4'):
            with open('htdocs' + filename, 'rb') as fin:
                return fin.read()
        if filename.endswith('.html') or filename == '/form' or filename == '/json':
            with open('htdocs' + filename) as fin:
                return fin.read()
    except FileNotFoundError:
        return 404


def handle_response(temp_content, msg):
    """Returns byte encoded HTTP response."""

    temp_response = ''

    # Build HTTP response
    try:
        filename = get_filename(msg)
        length = len(temp_content)
        if isinstance(temp_content, bytes) and filename.endswith('.jpg'):
            temp_response = 'HTTP/1.0 200 OK\nContent-Length: %d\nContent-Type: image/jpeg\n\n'. \
                                encode() % length
            temp_response += temp_content
        elif isinstance(temp_content, bytes) and filename.endswith('.png'):
            temp_response = 'HTTP/1.0 200 OK\nContent-Length: %d\nContent-Type: image/png\n\n'. \
                                encode() % length
            temp_response += temp_content
        elif isinstance(temp_content, bytes) and filename.endswith('.mp3'):
            temp_response = 'HTTP/1.0 200 OK\nContent-Length: %d\nContent-Type: audio/mp3\n\n'. \
                                encode() % length
            temp_response += temp_content
        elif isinstance(temp_content, bytes) and filename.endswith('.mp4'):
            temp_response = 'HTTP/1.0 200 OK\nContent-Length: %d\nContent-Type: video/mp4\n\n'. \
                                encode() % length
            temp_response += temp_content
        elif filename in ('/form', '/json'):
            temp_response = 'HTTP/1.0 200 OK\nContent-Length: %d\nContent-Type: application/json' \
                            '\n\n'.encode() % length
            temp_response += temp_content.encode()
        else:
            temp_response = 'HTTP/1.0 200 OK\nContent-Length: %d\nContent-Type: text/html\n\n'. \
                                encode() % length
            temp_response += temp_content.encode()
    except TypeError:
        pass

    if temp_content == 404:
        temp_response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'.encode()
    elif temp_content == 403:
        temp_response = 'HTTP/1.0 403 FORBIDDEN\n\nBad Request'.encode()
    elif temp_content == 400:
        temp_response = 'HTTP/1.0 400 BAD REQUEST\n\nBad Request'.encode()

    # Return encoded response
    return temp_response


class HTTPServer:
    """The HTTP/1.1 server."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.threads = []

    def start(self):
        """Starts the server."""
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print('Listening on port %s ...' % self.port)

        try:
            while True:
                # Accept client connections
                conn, address = self.sock.accept()

                # Starts the client connection thread
                thread = HTTPConnection(conn, address)
                thread.start()

                # Add to list
                self.threads.append(thread)

        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def stop(self):
        """Stops the server."""
        self.sock.close()
        for thread in self.threads:
            thread.stop()


class HTTPConnection(threading.Thread):
    """The HTTP/1.1 client connection."""

    def __init__(self, conn, address):
        super().__init__()
        self.conn = conn
        self.address = address
        self.active = True

    def stop(self):
        """Stops the client thread."""
        self.active = False
        self.conn.close()

    def run(self):
        """Handles the client connection."""

        while self.active:

            try:
                # Receive message
                msg = self.conn.recv(1024).decode()
                if get_close(msg):
                    break
                if msg:
                    print('Received:', msg)

                # Handle response
                request = handle_request(msg)
                res = handle_response(request, msg)

                # Send response
                self.conn.sendall(res)
            except OSError:
                pass
            except TypeError:
                pass

        # Close client connection
        print('Client disconnected...')
        self.conn.close()


if __name__ == '__main__':

    # Starts the http server
    server = HTTPServer('0.0.0.0', 8000)
    server.start()
