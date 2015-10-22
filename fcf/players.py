import uuid 

class CharType:
    spectator = 1
    frog = 2
    fly = 3
    general = 4

class Move:
    up = (-1, 0)
    down = (1, 0)
    left = (0, -1)
    right = (0, 1)


class Player(object):
    character = CharType.general
    playable = False 
    max_step_size = 0
    last_used_uuid = 0

    def __init__(self, name):
        self.uuid = Player.gen_uuid_debug()
        self.name = name
        self.next_move = None
        self.joined_time = None
        self.last_score_time = None
        self.score = 0

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
    character = CharType.frog
    playable = True
    max_step_size = 1

    def __init__(self, name):
        super(Frog, self).__init__(name)


class Fly(Player):
    character = CharType.fly
    playable = True
    max_step_size = 2

    def __init__(self, name):
        super(Fly, self).__init__(name)
    pass


class Spectator(Player):
    character = CharType.spectator
    def __init__(self, name):
        super(Spectator, self).__init__(name)
    pass
