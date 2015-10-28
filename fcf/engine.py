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
    

    def _free_cells(self):
        """ return list of free cells of board """
        ret = []
        for x in xrange(self.n):
            for y in xrange(self.m):
                if self.board[x][y] is None:
                    ret.append((x, y))
        return ret

    def _check_for_uuid(self, uuid):
        if uuid not in self.players:
            raise Exception('Unknown uuid:' + uuid)
    
    def _check_for_move(self, player, move):
        # move has to be l1, r2, d1 .. and so on
        if not len(move) == 2 or not (move[0] 
                in 'ldru' and move[1] in '12'):
            raise Exception('Unknown move type')

        if not player.playable:
            raise Exception('Player cannot make move')
        
        if int(move[1]) > player.max_step_size:
            raise Exception('char not able to move that long')
    
    def _inside(self, x, y):
        if x >= 0 and y >=0 and x < self.n and y < self.m:
            return True
        return False

    def _get_pos(self, uuid):
        # not efficient shouldn't be called inside a loop
        for x in xrange(self.n):
            for y in xrange(self.m):
                if self.board[x][y] == uuid:
                    return (x, y)

    @synchronized 
    def _update_state(self):
       
        # tuple of candidates, for each cell we have two candidates - one fly
        # and one frog (fly, frog). when two frogs are trying to occupy the
        # same board we give the priority who's timestamp is earlies same for
        # frogs

        candidates = [[[None,None] for _ in range(self.m)] for _ in range(self.n)]
        for x in xrange(self.n):
            for y in xrange(self.m):
                uuid = self.board[x][y]
                if uuid is None:
                    continue
                player = self.players[uuid]
                if not player.playable:
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
                        (not self.players[holder].char == player.char and
                        (compet is None or 
                        player.move_tstamp > self.players[compet].move_tstamp)))):
                    candidates[xto][yto][pos] = player.uuid
                else:
                    # player stays in the same cell
                    candidates[x][y][pos] = player.uuid
      
        # now waste flies update scores
        for x in xrange(self.n):
            for y in xrange(self.m):
                flid, frid = candidates[x][y]
                if flid and frid: # we have fly and frog at the same c
                    fl = self.players[flid] 
                    fr = self.players[frid]
                    fl.die()
                    fr.increase_score()
                    self.board[x][y] = frid
                elif not (flid or frid):
                    self.board[x][y] = None
                else: # we have only frog or fly
                    #if len(self.players) > 0 and self.players[1].char != Character.spectator:
                    #    import pdb; pdb.set_trace()
                    uid = frid if flid is None else flid
                    self.board[x][y] = uid

        # make last move stay, and check for timeouts
        for player in self.players.values():
            player.check_timeout()
            player.next_move = Move.stay


    def _game_loop(self):
        while True:
            self._update_state()
            time.sleep(self.frame_rate)
    
    def get_score(self, uuid):
        return self.players[uuid].score

    def _encode_board_for(self, player):
        spect = (player.char == Character.spectator)
        if not spect:   # position of current player
            px, py = self._get_pos(player.uuid)
        ret = ''
        for x in xrange(self.n):
            for y in xrange(self.m):
                if not spect and max(abs(x - px), abs(y - py)) > player.max_step_size:
                    ret += Symbol.dark
                elif not spect and (x, y) == (px, py):
                    ret += Symbol.me
                elif self.board[x][y] is None:
                    ret += Symbol.empty
                elif self.players[self.board[x][y]].char == Character.frog:
                    ret += Symbol.frog
                else:
                    ret += Symbol.fly
        return ret

    def vis_area(self, uuid):
        """ return whole board concatenated into chars"""
        
        #TODO bit more  hardcoding, to refactore later
        self._check_for_uuid(uuid)
        player = self.players[uuid]
        #import pdb; pdb.set_trace()
        return self._encode_board_for(player)

    
    @synchronized 
    def add_player(self, name):
        spect = Spectator(name) # new player is a spectator
        self.players[spect.uuid] = spect
        logging.debug('added player %s with uuid %s' % (name, spect.uuid))
        return spect.uuid
    
    
    @synchronized
    def join_game(self, uuid, char_type):
        """ uuid and char_type - 'fr' for frog and 'fl' for fly """
        
        self._check_for_uuid(uuid)
        spectator =  self.players[uuid]
        if not spectator.char == Character.spectator:
            raise Exception('Player is not a spectator')

        if char_type == 'fr':  
            player = Frog.from_player(spectator)
        elif char_type == 'fl':
            player = Fly.from_player(spectator)
        else:
            raise Exception('char type not recogniszed')

        cells = self._free_cells()
        if len(cells) == 0:
            raise Exception('There is no empty place on a board')

        player.joined_time = time.time()
        player.score = 0
        player.last_score_time = time.time()
        pos = random.choice(cells)
        self.board[pos[0]][pos[1]] = player.uuid
        self.players[player.uuid] = player
    
    @synchronized
    def set_next_move(self, uuid, move, timestamp):
        # set move u1, d2, l1 and so on for player with uuid
        # and update timestamp of this move
        self._check_for_uuid(uuid) 
        player = self.players[uuid]
        self._check_for_move(player, move)
        d = move[0] # direction
        c = int(move[1]) # step

        if d == 'u':
            mv = Move.up
        elif d =='d':
            mv = Move.down
        elif d == 'l':
            mv = Move.left
        elif d == 'r':
            mv = Move.right
        else:
            raise Exception('unrecognized move')
         
        player.next_move = (mv[0] * c, mv[1] * c)
        #import pdb; pdb.set_trace()
        player.move_tstamp = timestamp

    def run(self):
        self.loop_thread.start()
