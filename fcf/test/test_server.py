
import unittest
from fcf.server import Server

class FakeEngine(object):
    def __init__(self):
        pass

    def add_player(self, name):
        return 42


class Test(unittest.TestCase):
    
    def setUp(self):
        self.server = Server(10, 10)
    
    def test_run_suc(self):
        self.server.run()
