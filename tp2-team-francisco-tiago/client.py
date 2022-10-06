"""
 Simple socket client

"""

import socket


class Client:
    """The chat client."""

    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))

    def command(self, msg):
        """Sends a command and returns response"""
        self.sock.sendall(msg.encode())
        return self.sock.recv(1024).decode()

    def close(self):
        """Closes the connection."""
        self.sock.close()

    def start(self):
        """Start the command loop."""
        msg = input('Command > ')
        self.sock.sendall(msg.encode())
        res = self.command(msg)
        print(res)
        while msg != '/exit':
            # Sends a command
            msg = input('> ')
            res = self.command(msg)
            print(res)

            # Check for termination
            if msg == '/exit':
                break


if __name__ == "__main__":
    # Starts the client
    client = Client('127.0.0.1', 8000)
    client.start()
    client.close()
