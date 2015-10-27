import time
import random
import threading
from functools import wraps
from fcf.players import *


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
    def __init__(self, n, m, fr=0.5):
        # store players in dict using uuid
        self.players = {}
        self.board = [[None for _ in range(m)] for _ in range(n)]
        self.n = n
        self.m = m
        self.frame_rate = fr
        self.lock = threading.Lock()
    

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
            raise Exception('Unknown uuid')
    
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
        if x >= 0 and y >=0 and x < n and y < m:
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

        candidates = [[(0,0) for _ in range(self.m)] for _ in range(self.n)]
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
                xto, yto = psum(player.next_move, (x, y))
                
                inside = self._inside(xto, yto)
                holder = self.board[xto][yto] if inside else None
                compet = candidates[xto][yto][pos] # competitior with cell
                if (inside and holder is None or 
                        (not self.players[holder].char == player.char and
                        player.move_tstamp > self.players[compet].move_tstamp)):
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
                    fr.increase_point()
                    self.board[x][y] = frid
                elif not (flid or frid):
                    self.board[x][y] = None
                else: # we have only frog or fly
                    uid = frid if flid is None else flid
                    self.board[x][y] = uid
                    self.players[uid].check_timeout()

        # make last move stay
        for player in self.players.values():
            player.next_move = Move.stay


    def _game_loop(self):
        self._update_state()
        time.sleep
    
    def get_score(self, uuid):
        return self.players[uuid].score
     
    def vis_area(self, uuid):
        """ return whole board concatenated into chars"""
        # 0 - area hidden
        # 1 - players location
        # 2 - frog
        # 3 - fly
        # 4 - area visible, cell empty
        
        #TODO bit more  hardcoding, to refactore later
        self._check_for_uuid(uuid)
        player = self.players[uuid]
        (px, py) = self._get_pos(uuid)
        ret = ''
        for x in xrange(self.n):
            for y in xrange(self.m):
                if max(abs(x - px), abs(y - py)) > player.max_step_size:
                    ret += '0'
                elif (x, y) == (px, py):
                    ret += '1'
                elif self.board[x][y] is None:
                    ret += '4'
                elif self.players[self.board[x][y]].char == Character.frog:
                    ret += '2'
                else:
                    ret += '3'
        return ret

    
    @synchronized 
    def add_player(self, name):
        spect = Spectator(name) # new player is a spectator
        self.players[spect.uuid] = spect
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
        player.move_tstamp = timestamp
