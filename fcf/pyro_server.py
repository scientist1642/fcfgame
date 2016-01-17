import Pyro4
from engine import *
import logging
import signal
import sys
from multiprocessing import Process, Queue, Value, Manager
from threading import Thread
import socket
import ctypes

# Board Size
SERVER_UPD_PORT = 7782
BROADCAST_INTERVAL = 5
signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

class Server():
    
    def __init__(self, n, m):
        self.pyro_proc = None
        self.broadcast_proc = None
        self.broadcast_sock = None
        self.n = n
        self.m = m
        self.uri = None # Pyro uri

    def _pyro_loop(self, n, m,d):
        print "starting pyro loop"
        daemon = Pyro4.Daemon(host='25.63.229.152')
        game = Engine(n, m)
        game.run()
        d[1] = daemon.register(game, "server.game").asString()
        print "pyro server : " + d[1]
        daemon.requestLoop()
        """Pyro4.Daemon.serveSimple(
                {
                    game: "server.game"
                },
                daemon = pyrodaemon,
                ns = False)
        """

    def _broadcast_loop(self, sock, uri):     
        print "starting broadcast loop"
        while True:
            payload = 'fcfgame|' + uri
            print 'Broadcasting... ' + payload
            sock.sendto(payload, ('255.255.255.255', SERVER_UPD_PORT))
            time.sleep(BROADCAST_INTERVAL)

    def start_server(self):
        """create game """
        manager = Manager()
        d = manager.dict()
        #uri_val = Value(ctypes.c_char_p)
        self.pyro_proc = Process(target=self._pyro_loop, args=(self.n, self.m, d))
        
        # main loop (gui) is blocked until pyro is initialized bad idea
        # but should do for now

        self.pyro_proc.start()

         
        
        time.sleep(2)
        #print 'uri_val is', uri_val.value
        if not 1 in d:
            raise Exception('pyro failed to initalize in short time')
        self.uri = d[1]
    
        # also start broadcasting
        self.broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.broadcast_sock.bind(('', SERVER_UPD_PORT))

        self.broadcast_proc = Thread(target = self._broadcast_loop, 
                args=(self.broadcast_sock, self.uri))
        self.broadcast_proc.start()

    def stop_server(self):
        #try:
        self.broadcast_sock.close()
        self.broadcast_proc.terminate()
        self.pyro_proc.terminate()
        #except Pyro4.error.CommunicationErrorr as e:
        #    print 'connection error occured'
        #    pass

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
