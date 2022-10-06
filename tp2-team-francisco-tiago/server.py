"""
 Simple multi-threaded socket server

"""

import socket
import threading
import functions as f


class Server:
    """The chat server."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.users_rooms = {}
        self.rooms = ['welcome']
        self.rooms_msg_queue = ['']
        self.users_pmsg = {}

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
                conn, _ = self.sock.accept()

                # Starts client thread
                thread = threading.Thread(target=handle_client, args=(conn,
                                                                      self.users_rooms,
                                                                      self.rooms,
                                                                      self.rooms_msg_queue,
                                                                      self.users_pmsg))
                thread.start()

        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def stop(self):
        """Stops the server."""
        self.sock.close()


def handle_client(conn, users_rooms, rooms, rooms_msg_queue, users_pmsg):
    """Handles the client connection"""

    queue_pos = [0]

    res = 'Unknown Command'
    username = ''
    while username == '':
        try:
            msg = conn.recv(1024).decode()
        except ConnectionAbortedError:
            break
        except ConnectionResetError:
            break
        if msg.startswith('/username '):
            username = msg[10: None]
            res = f.username(users_rooms, username, users_pmsg)
        else:
            res = '/username required'
            conn.sendall(res.encode())

    try:
        conn.sendall(res.encode())
    except ConnectionAbortedError:
        pass
    except ConnectionResetError:
        pass

    while True:
        # Receive message
        try:
            msg = conn.recv(1024).decode()
        except ConnectionAbortedError:
            break
        except ConnectionResetError:
            break

        if msg == '/rooms':
            res = f.rooms(rooms)
        elif msg == '/room':
            res = f.room(users_rooms, username, rooms)
        elif msg.startswith('/create '):
            room = msg[9: None]
            res = f.create_room(rooms, room, rooms_msg_queue, queue_pos)
        elif msg.startswith('/join '):
            room = msg[7: None]
            res = f.join_room(username, users_rooms, rooms, room)
        elif msg == '/users':
            res = f.users(username, users_rooms)
        elif msg == '/allusers':
            res = f.all_users(users_rooms, rooms)
        elif msg == '/msgs':
            res = f.msgs(users_rooms, username, rooms_msg_queue, queue_pos)
        elif msg.startswith('/msg '):
            res = f.msg(users_rooms, username, rooms, rooms_msg_queue, msg[5: None])
        elif msg.startswith('/pmsg '):
            temp_list = msg.split()
            res = f.pmsg(temp_list[1], users_pmsg, temp_list[2], username)
        elif msg == '/pmsgs':
            res = f.pmsgs(username, users_pmsg)
        elif msg == '/exit':
            res = '/exit ok'
            conn.sendall(res.encode())
            break

        # Send response
        conn.sendall(res.encode())

    # Close client connection
    print('Client disconnected...')
    f.remove_user(username, users_rooms, users_pmsg)
    conn.close()


if __name__ == "__main__":
    # Starts the server
    server = Server('0.0.0.0', 8000)
    server.start()
