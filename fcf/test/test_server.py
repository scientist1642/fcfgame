import unittest
from fcf.server import Server

class FakeEngine(object):
    def __init__(self):
        pass

    def add_player(self, name):
        return 42

    def get_score(self, uuid):
        pass

    def vis_area(self, uuid):
        pass

    def join_game(self, uuid, char_type):
        pass

    def set_next_move(self, uuid, move, timestamp):
        pass


class Test(unittest.TestCase):
    
    def setUp(self):
        self.server = Server(10, 10)
    
    def test_run_suc(self):
        self.server.run()
