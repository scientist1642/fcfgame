import unittest
from fcf.players import *

class Test(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_from_player(self):
        name = 'kenny'
        spectator = Spectator(name)
        uuid = spectator.uuid
        self.assertEqual(spectator.character, CharType.spectator)

        frog = Frog.from_player(spectator)
        self.assertEqual(frog.name, name)
        self.assertEqual(frog.character, CharType.frog)
        self.assertEqual(frog.uuid, uuid)




