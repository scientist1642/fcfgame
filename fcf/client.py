import socket
import threading

IN_BUF_SIZE = 256
SERVER_PORT = 7777

class Command:
    newplayer = 1
    chooseplayer = 2
    move = 3


class Response:
    data = 1
    shutdown = 2


class Client:
    def __init__(self):
        self.name = None
        self.server_addr = None
        self.serv_sock = None
        self.board = None
        self.score = None

    def get_score(self):
        return self.score

    def ger_board(self):
        return self.board

    def set_server_ip(self, addr):
        self.server_addr = addr

    def set_name(self, name):
        self.name = name

    def set_move(self, str):
        self._send_Msg_to_server(Command.move)
        self._send_Msg_to_server(str)

    def choose_player(self, str):
        self._send_Msg_to_server(Command.chooseplayer)
        self._send_Msg_to_server(str)

    def run(self):
        self._connect_to_server()
        t = threading.Thread(target=self._proc_responce)
        t.start()

    def _send_Msg_to_server(self, msg):
        if self.serv_sock != None:
            try:
                self.serv_sock.send(msg)
            except:
                pass

    def _connect_to_server(self):
        try:
            if (self.server_addr != None and self.name != None):
                self.serv_sock = socket.create_connection((self.server_addr, SERVER_PORT))
                self.serv_sock.send(Command.newplayer)
                self.serv_sock.send(self.name)
        except:
            #handle error
            pass

    def _proc_responce(self, ):
        while True:
            if self.serv_sock != None:
                resp = self.serv_sock.recv(1)
                if resp == Response.data:
                    data = self.serv_sock.recv(IN_BUF_SIZE).split()
                    self.board = data[0].strip()
                    self.score = data[1].strip()

                if resp == Response.shutdown:
                    pass
                    break
