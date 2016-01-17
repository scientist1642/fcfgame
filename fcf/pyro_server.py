import Pyro4
from engine import *
import logging
import sys
from multiprocessing import Process, Queue
from pyro_client import SERVER_UPD_PORT
import socket

# Board Size
N = 10
M = 13 

BROADCAST_INTERVAL = 5


class Server():
    
    def __init__(self, n, m):
        self.pyro_proc = None
        self.broadcast_proc = None
        self.broadcast_sock = None
        self.n = n
        self.m = m
        self.uri = None # Pyro uri

    def _pyro_loop(self, daemon, n, m):
        print "starting pyro loop"
        game = Engine(N, M)
        game.run()
        print uri
        daemon.requestLoop()
        """Pyro4.Daemon.serveSimple(
                {
                    game: "server.game"
                },
                daemon = pyrodaemon,
                ns = False)
        """

    def _broadcast_loop(self, sock):     
        while True:
            data = repr(time.time()) + '\n'
            s.sendto(data, ('255.255.255.255', MYPORT))
            time.sleep(BROADCAST_INTERVAL)

    def start_server(self,n, m):
        """create game """
        daemon = Pyro4.Daemon(host='25.63.229.152')
        self.uri = daemon.register(game, "server.game")
        self.pyro_proc = Process(target=self._pyro_loop, args=(daemon, self.n, self.m))
        self.pyro_proc.start()

         
        # also start broadcasting
        self.broadcast_sock = socket(AF_INET, SOCK_DGRAM)
        self.broadcast_sock.bind(('', SERVER_UPD_PORT))
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.broadcast_proc = Process(target = self._broadcast_loop, 
                args=(self.broadcast_sock,))

        
        while True:
            r = raw_input()
            print r
        return
    
    def stop_server(self):
        self.broadcast_sock.close()
        self.broadcast_proc.kill()
        self.pyro_proc.kill()

"""
if __name__ == '__main__':
    #instantiate game engine and run pyro daemon
    game = Engine(N, M)
    game.run()
    pyrodaemon = Pyro4.Daemon(host='25.63.229.152')
    uri = pyrodaemon.register(game, "server.game")
    print uri
    pyrodaemon.requestLoop()



    Pyro4.Daemon.serveSimple(
            {
                game: "server.game"
            },
            daemon = pyrodaemon,
            ns = False)
"""
