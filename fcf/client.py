import sys
import socket

class Command:
    newplayer = 1
    chooseplayer = 2
    move = 3

class Response:
    data = 1
    shutdown = 2

def read_args():
    """ Read name and server address from command line """
    if len(sys.argv) <= 2:
        sys.stderr.write(u'Usage: %s <client name> <game server>\n' % sys.argv[0])
        sys.exit(1)

    return sys.argv[1], sys.argv[2]

SERVER_PORT = 7777

class Client:
    def __init__(self, name, server_addr):
        self.name = name
        self.server_addr = server_addr
        self.serv_socket = None

    def _vizualize(self):
        pass

    def _connect_to_server(self):
        try:
            self.serv_socket = socket.create_connection((server_addr, SERVER_PORT))
            self.serv_socket.send(Command.newplayer)
            self.serv_socket.send(self.name)
        except:
            #handle error
            pass

    def run(self):
        self._connect_to_server()
        while True:
            #process client input

            pass

if __name__ == '__main__':
    name, server_addr = read_args()
    client = Client(name, server_addr)

