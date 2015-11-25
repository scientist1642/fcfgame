import logging
import sys
import Pyro4


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

    def connect(self):
        if self.uri is None:
            raise Exception('uri not set')
        if self.name is None:
            raise Exception('name not set')

        try:
            self.game = Pyro4.Proxy(self.uri)
        except Exception, e:
            logging.error('Couldn"t get a game object')
            raise e
        self.player = self.game.register(self.name)

    def get_score(self):
        self.player.get_score()

    def get_board(self):
        logging.debug('board requested returned:')
        return self.player.get_vis_area()

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

    def choose_player(self, char):
        self.player.join_game(char)

