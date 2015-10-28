import sys
import socket
import threading
import logging


IN_BUF_SIZE = 256
SERVER_PORT = 7777

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
class Command:
    newplayer = '1'
    chooseplayer = '2'
    move = '3'
    board = '4'


class Response:
    data = '1'
    shutdown = '2'
    error = '3'


class Client:
    def __init__(self):
        self.name = None
        self.server_addr = None
        self.serv_sock = None
        self.board = None
        self.score = None

    def get_score(self):
        return self.score

    def get_board(self):
        logging.debug('board requested returned:')
        return self.board

    def set_server_ip(self, addr):
        self.server_addr = addr
        logging.debug('ip address provided ')

    def set_name(self, name):
        self.name = name
        logging.debug('user name provided : ')

    def set_move(self, move):
        self._send_Msg_to_server(Command.move)
        self._send_Msg_to_server(move)

    def choose_player(self, char):
        self._send_Msg_to_server(Command.chooseplayer)
        self._send_Msg_to_server(char)

    def run(self):
        #import pdb; pdb.set_trace()
        self._connect_to_server()
        logging.debug('connected to server')
        t = threading.Thread(target=self._proc_responce)
        t.start()

    def _send_Msg_to_server(self, msg):
        if self.serv_sock != None:
            try:
                self.serv_sock.send(msg)
            except:
                raise

    def _connect_to_server(self):
        try:
            logging.debug('trying to connect server at ' + self.server_addr)
            if (self.server_addr != None and self.name != None):
                self.serv_sock = socket.create_connection((self.server_addr, SERVER_PORT))
                self.serv_sock.send(Command.newplayer)
                self.serv_sock.send(self.name)
        except:
            #handle error
            raise

    def _proc_responce(self, ):
        while True:
            if self.serv_sock != None:
                resp = self.serv_sock.recv(1)
                if resp == Response.data:
                    data = self.serv_sock.recv(IN_BUF_SIZE).split(':')
                    self.board = data[0].strip()
                    self.score = data[1].strip()

                if resp == Response.shutdown:
                    pass
                    break
                
                if resp == Response.error: 
                    data = self.serv_sock.recv(IN_BUF_SIZE)
                    logging.error(data)
