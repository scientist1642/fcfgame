# Client in a sense now means - a client of frontend, this code 
# is also responsible for starting a server if it needs to.
import logging
import sys
import Pyro4
import time
from multiprocessing import Process, Manager
from threading import Thread, Event
import socket
from pyro_server import Server

# port to listen to server updates
SERVER_UPD_PORT = 7782
MAX_UPD_INTERVAL = 15

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
class Client:
    def __init__(self):
        self.name = None
        self.server_addr = None
        self.serv_sock = None
        self.board = None
        self.score = None
        self.player = None
        self.game = None
        manager = Manager()
        self.aval_servers = manager.dict()
        self.update_proc = None # process to update available servers
        self.update_sock  = None # socket to listen for broadcast
        self.server = Server(10, 13)
        self.game_started = False
        self.stop_upd_event = Event()

    def connect(self):
        if self.uri is None:
            raise Exception('uri not set')
        if self.name is None:
            raise Exception('name not set')

        try:
            print('trying to get proxy object')
            self.game = Pyro4.Proxy(self.uri)
            logging.warn(self.uri)
        except Exception, e:
            logging.error('Couldn"t get a game object')
            raise e
        self.player = self.game.register(self.name)

    def get_score(self):
        return self.player.get_score()

    def get_board(self):
        logging.debug('board requested returned:')
        try:
            vis_area = self.player.get_vis_area()
        except Pyro4.errors.PyroError as e:
            vis_area = None
            logging.error('connection errror occured\n' + str(e))
            pass
        #print vis_area
        return  vis_area

    def set_uri(self, uri):
        self.uri = uri
        logging.debug('address provided ')

    def set_name(self, name):
        self.name = name
        logging.debug('user name provided : ')

    def set_move(self, move):
        if self.player:
            self.player.set_next_move(move)

    def disconnect(self):
        # if a user disconnects we kill a character
        self.player.die()

    def _update_aval_servers(self, sock, aval_servers, stop_event):
        while True:
            try:
                server_uri = sock.recv(1024)
                if server_uri.startswith('fcfgame|'):
                    _, server_uri = server_uri.split('|', 1)
                    aval_servers[server_uri] = time.time()
                logging.debug( 'received server' + server_uri)
            except socket.timeout, e:    
                if stop_event.is_set():
                    logging.warn('exiting updating server loop')
                    return
            #logging.debug('received server %s' % (server_uri,))

            # to check we reveive expected messages
            


    def choose_player(self, char):
        self.player.join_game(char)

    def get_aval_servers(self):
        # check for outdated servers
        to_delete = []
        for serv, upd_time in self. aval_servers.items():
            if time.time() - upd_time > MAX_UPD_INTERVAL:
                to_delete.append(serv)

        for serv in to_delete:
            del self.aval_servers[serv]
        return self.aval_servers.keys()

    def start_updating_servers(self):
        self.update_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.update_sock.bind(('', SERVER_UPD_PORT))
        self.update_sock.settimeout(0.5)
        self.update_proc = Thread(target=self._update_aval_servers, 
                args=(self.update_sock, self.aval_servers, self.stop_upd_event))
        self.stop_upd_event.clear()
        self.update_proc.start()

    def stop_updating_servers(self):
        print "stopping updating servers"
        self.stop_upd_event.set()
        time.sleep(0.6)
        #self.update_sock.shutdown(socket.SHUT_WR)
        self.update_sock.close()
        #self.update_proc_event.set()

    def start_server(self):
        self.server.start_server()

    def stop_server(self):
        self.game_started = False
        self.server.stop_server()
