import time
import random
from fcf.players import *


class Engine:
    def __init__(self, n, m):
        # store players in dict using uuid
        self.players = {}
        self.board = [[None for _ in range(m)] for _ in range(n)]
        self.n = n
        self.m = m
    
    def add_player(self, name):
        spect = Spectator(name) # new player is a spectator
        self.players[spect.uuid] = spect
        return spect.uuid

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
            raise Exception('Character not able to move that long')
  

    def join_game(self, uuid, character_type):
        """ uuid and char_type - 'fr' for frog and 'fl' for fly """
        
        self._check_for_uuid(uuid)
        spectator =  self.players[uuid]
        if not spectator.character == CharType.spectator:
            raise Exception('Player is not a spectator')

        if character_type == 'fr':  
            player = Frog.from_player(spectator)
        elif character_type == 'fl':
            player = Fly.from_player(spectator)
        else:
            raise Exception('Character type not recogniszed')

        cells = self._free_cells()
        if len(cells) == 0:
            raise Exception('There is no empty place on a board')

        player.joined_time = time.time()
        player.score = 0
        pos = random.choice(cells)
        self.board[pos[0]][pos[1]] = player.uuid
        self.players[player.uuid] = player

    def set_next_move(self, uuid, move):
        # set move u1, d2, l1 and so on for player
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
