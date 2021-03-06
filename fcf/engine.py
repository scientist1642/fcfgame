import sys
import time
import random
import threading
from functools import wraps
from players import *
import logging


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

# symbols used to decode/encode board 
class Symbol(object):
    dark = '0' # can't see the board
    me = '1'
    empty = '2'
    frog = '3'
    fly = '4'


def synchronized(func):
    @wraps(func)
    def with_lock(self, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return with_lock

def psum(a, b):
    """ returns pairwise sum of tuples or arrays"""
    return type(a)(map(sum,zip(a,b)))


class Engine:
    def __init__(self, n, m, fr=0.2):
        # store players in dict using uuid
        self.players = {}
        self.board = [[None for _ in range(m)] for _ in range(n)]
        self.n = n
        self.m = m
        self.frame_rate = fr
        self.lock = threading.Lock()
        self.loop_thread = threading.Thread(target=self._game_loop)
    
    def register(self, name):
        try:
            print 'registering ' + name
            player = Spectator(name, self) # new player is in spectator mode
            self.players[player.uuid] = player
            logging.debug('added player %s with uuid %s' % (name, player.uuid))
            self._pyroDaemon.register(player) # expose it via pyro
            return player
        except AttributeError:
            raise Exception('No Daemon is running to register a player')

    def place_at_random(self, player):
        # places a new player at random cell
        cells = self._free_cells()
        if len(cells) == 0:
            logging.error('There is no empty place on a board')
            raise
        
        pos = random.choice(cells)
        self.board[pos[0]][pos[1]] = player
        self.players[player.uuid] = player

    def remove_player(self, player):
        #del self.players[player.uuid]
        for x in xrange(self.n):
            for y in xrange(self.m):
                if self.board[x][y] == player:
                    self.board[x][y] = None

    def _free_cells(self):
        """ return list of free cells of board """
        ret = []
        for x in xrange(self.n):
            for y in xrange(self.m):
                if self.board[x][y] is None:
                    ret.append((x, y))
        return ret
    
    def _inside(self, x, y):
        if x >= 0 and y >=0 and x < self.n and y < self.m:
            return True
        return False
    
    
    @synchronized 
    def _update_state(self):
       
        # tuple of candidates, for each cell we have two candidates - one fly
        # and one frog (fly, frog). when two frogs are trying to occupy the
        # same board we give the priority who's timestamp is earlies same for
        # frogs

        candidates = [[[None,None] for _ in range(self.m)] for _ in range(self.n)]
        for x in xrange(self.n):
            for y in xrange(self.m):
                """uuid = self.board[x][y]
                if uuid is None:
                    continue
                player = self.players[uuid]"""
                player = self.board[x][y]
                if player is None or not player.playable:
                    continue
                # position of characters in the tuple
                if player.char == Character.fly:
                    pos = 0
                elif player.char == Character.frog:
                    pos = 1
                # nove we want to update number of chars on the cell,
                # this player is trying to move
                xto, yto = psum(player.next_move, [x, y])
                
                inside = self._inside(xto, yto)
                holder = self.board[xto][yto] if inside else None
                compet = candidates[xto][yto][pos] if inside else None # competitior with cell
                if (inside and (holder is None or 
                        (not holder.char == player.char and
                        (compet is None or 
                        player.move_tstamp > compet.move_tstamp)))):
                    candidates[xto][yto][pos] = player
                else:
                    # player stays in the same cell
                    candidates[x][y][pos] = player

        # now waste flies update scores
        for x in xrange(self.n):
            for y in xrange(self.m):
                fl, fr = candidates[x][y]
                if fl and fr: # we have fly and frog at the same c
                    fl.die()
                    fr.increase_score()
                    self.board[x][y] = fr
                elif not (fl or fr):
                    self.board[x][y] = None
                else: # we have only frog or fly
                    self.board[x][y] = fl or fr

        # make last move stay, and check for timeouts
        for player in self.players.values():
            player.check_timeout()
            player.next_move = Move.stay


    def _game_loop(self):
        while True:
            self._update_state()
            time.sleep(self.frame_rate)

    def _get_pos(self, player):
        for x in xrange(self.n):
            for y in xrange(self.m):
                if player == self.board[x][y]:
                    return (x, y)
    
    def _encode_board_for(self, player):
        spect = (player.char == Character.spectator)
        if not spect:   # position of current player
            # TODO just player._get_pos
            px, py = self._get_pos(player)
        ret = ''
        for x in xrange(self.n):
            for y in xrange(self.m):
                if not spect and max(abs(x - px), abs(y - py)) > player.max_look:
                    ret += Symbol.dark
                elif not spect and (x, y) == (px, py):
                    ret += Symbol.me
                elif self.board[x][y] is None:
                    ret += Symbol.empty
                elif self.board[x][y].char == Character.frog:
                    ret += Symbol.frog
                else:
                    ret += Symbol.fly
        return ret
    
    def run(self):
        self.loop_thread.start()
