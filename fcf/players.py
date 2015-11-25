import time
import uuid 


class Character:
    spectator = 1
    frog = 2
    fly = 3
    general = 4

class Move:
    up = (-1, 0)
    down = (1, 0)
    left = (0, -1)
    right = (0, 1)
    stay = (0, 0)


class Player(object):
    char = Character.general
    playable = False 
    max_step = 0
    max_look = 0
    last_used_uuid = 0

    def __init__(self, name, game):
        self.uuid = Player.gen_uuid_debug()
        self.name = name
        self.game = game
        self.next_move = Move.stay
        self.move_tstamp = None
        self.joined_time = None
        self.last_score_time = None
        self.score = 0
    
    def join_game(self, char_type):
        with self.game.lock:
            if char_type == 'fr':
                self.__class__ = Frog
            elif char_type == 'fl':
                self.__class__ = Fly
            else:
                raise Exception('char type not recogniszed')

            self.joined_time = time.time()
            self.score = 0
            self.last_score_time = time.time()
            self.game.place_at_random(self)

    def get_vis_area(self):
        return self.game._encode_board_for(self)

    def get_score(self):
        return self.score

    def set_next_move(self, move):
        with self.game.lock:
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
                print 'unrecognized move'                
                return
            
            self.next_move = (mv[0] * c, mv[1] * c)
            self.move_tstamp = time.time()

    def increase_score(self):
        self.score += 1
        self.last_score_time = time.time()

    def die(self):
        self.score = 0
        self.game.remove_player(self)
        self.__class__ = Spectator
    
    def check_timeout(self):
        pass


    @classmethod
    def from_player(cls, player):
        """ Factory method to create a certain character from other, i.e. frog
        from spectator """
        ret_obj = cls(player.name)
        ret_obj.uuid = player.uuid
        ret_obj.score = 0
        return ret_obj

    @classmethod
    def gen_uuid_debug(cls):
        cls.last_used_uuid += 1
        return cls.last_used_uuid
    
    @classmethod
    def gen_uuid_prod():
        return uuid.uuid1()



class Frog(Player):
    char = Character.frog
    playable = True
    max_step = 2
    max_look = 1
    timeout = 2 * 60 # 2 min

    def __init__(self, name, game):
        super(Frog, self).__init__(name, game)

    def check_timeout(self):
        # for frog if it doesn't eat anything for 2 minutes it will die
        if (self.last_score_time is not None and 
                time.time() - self.last_score_time > Frog.timeout):
            self.die()



class Fly(Player):
    char = Character.fly
    playable = True
    max_step = 1
    max_look = 2
    timeout = 2 * 60 # 2 min

    def __init__(self, name, game):
        super(Fly, self).__init__(name, game)
    pass
    
    def check_timeout(self):
        # for frog if it doesn't eat anything for 2 minutes it will die
        if (self.last_score_time is not None and 
                time.time() - self.last_score_time > Fly.timeout):
            self.increase_score()


class Spectator(Player):
    char = Character.spectator
    def __init__(self, name, game):
        super(Spectator, self).__init__(name, game)
    pass
