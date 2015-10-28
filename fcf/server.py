import socket
from engine import *
import logging
import sys
import threading
import time

PORT = 7777
MAX_QUEUED_CONS = 100
IN_BUF_SIZE = 200

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

class Server:
    """ Serve the client using engine API """
    def __init__(self, n, m, feed_rate=0.2):
        self.socket = self._create_server_socket()
        self.game_engine = Engine(n, m)
        self.clients_socks = {}
        self.threads = []
        self.n = n
        self.m = m
        self.feed_rate = feed_rate#seconds
        self.game_engine.run()

    def _create_server_socket(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", PORT))
        server_sock.listen(MAX_QUEUED_CONS)
        return server_sock

    def _send_Msg(self, cl_sock, msg, r_code):
        cl_sock.send(r_code + msg)

    def _send_cl_data(self, cl_sock, uuid):
        area = self.game_engine.vis_area(uuid)
        #import pdb; pdb.set_trace()
        score = self.game_engine.get_score(uuid)
        msg = area + ":" + str(score)
        self._send_Msg(cl_sock, msg, Response.data)

    def _send_response(self, cl_sock, response):
        try:
            self._send_Msg(cl_sock, response)
        except:
            for uuid, sock in self.clients_socks.iteritems():
                if sock == cl_sock:
                    del self.clients_socks[uuid]

    def _feed_client(self, cl_sock, uuid):
        while True:
            try:
                self._send_cl_data(cl_sock, uuid)
            except socket.error, e:
                logging.debug(e)
                break
            time.sleep(self.feed_rate)

    def _process_request(self, cl_sock):
        uuid = None
        while True:
            com = cl_sock.recv(1)
            if (com == Command.newplayer):
                if uuid is not None:
                    self._send_Msg(cl_sock, 'you have already registered', 
                            Response.error)
                    continue
                else:
                    name = cl_sock.recv(IN_BUF_SIZE)
                    uuid = self.game_engine.add_player(name)
                    logging.debug('player %s was connected' % (name))
                    self.clients_socks[uuid] = cl_sock
                    t_feeder = threading.Thread(target=self._feed_client, args=(cl_sock, uuid))
                    t_feeder.start()
                    self.threads.append(t_feeder)

            if (com == Command.chooseplayer):
                if uuid is None:
                    self._send_Msg(cl_sock, 'you have to register first', Response.error)
                    continue
                else:
                    character_type = cl_sock.recv(2)
                    self.game_engine.join_game(uuid, character_type)

            if (com == Command.move):
                if uuid is None:
                    self._send_Msg(cl_sock, Response.error + 'you have to register first')
                    continue
                else:
                    move = cl_sock.recv(2)
                    time_stamp = int(round(time.time() * 1000))
                    try:
                        self.game_engine.set_next_move(uuid, move, time_stamp)
                    except Exception, e:
                        logging.error(str(e))


    def run(self):
        """ Run main server loop which will accept clients """
        logging.debug('Server is running...')
        while True:
            clientsock, addr = self.socket.accept()
            logging.debug('accepting new connection...')
            t = threading.Thread(target=self._process_request, args=(clientsock, ))
            t.start()
            self.threads.append(t)

    def shutdown(self):
        """ Instruct all clients before closing connections """
        for uuid in self.clients_socks:
            cl_sock = self.clients_socks[uuid]
            self._send_response(cl_sock, Response.shutdown)
            cl_sock.send("Server need to shutdown")
            self._send_Msg(cl_sock, Response.data + str(e))

        for thread in self.threads:
            thread.join()

        self.socket.close()
        del self.threads
        self.clients_socks.clear()

if __name__ == '__main__':
    server = Server(10, 11)
    try:
        server.run()
    except (KeyboardInterrupt, SystemExit):
        server.socket.close()
        raise

