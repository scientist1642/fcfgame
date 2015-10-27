import unittest
from fcf.engine import *

class Test(unittest.TestCase):
    
    def setUp(self):
        self.engine = Engine(4, 4, 0.5)

    def test_add_player(self):
        name = 'kenny'
        uuid = self.engine.add_player(name)
        self.assertIsNotNone(uuid)
        self.assertIn(uuid, self.engine.players)
        self.assertEqual(self.engine.players[uuid].name, name)
    
    def test_join_game_excep(self):
        # test for unknown uuid
        
        #TODO check for raised exceptions i.e self.assertRaises
        pass
    
    def join_kenny_as_frog(self):
        name = 'kenny'
        uuid = self.engine.add_player(name)
        self.engine.join_game(uuid, 'fr') 
        return uuid

    def join_cartman_as_fly(self):
        name = 'cartman'
        uuid = self.engine.add_player(name)
        self.engine.join_game(uuid, 'fl') 
        return uuid
    
    def test_join_game_success(self):
        name = 'kenny'
        uuid = self.join_kenny_as_frog()
        self.assertEqual(len(self.engine.players), 1) # still only 1 player
        kenny = self.engine.players[uuid]
        self.assertEqual(kenny.character, CharType.frog)
        self.assertEquals(kenny.name, name)

    def test_move_success(self):
        uuid = self.join_kenny_as_frog()
        self.engine.set_next_move(uuid, 'u1')
        kenny = self.engine.players[uuid]
        self.assertEquals(kenny.next_move, (-1, 0))

    def test_fly_move_success(self):
        uuid = self.join_cartman_as_fly()
        self.engine.set_next_move(uuid, 'l2')
        cartman = self.engine.players[uuid]
        self.assertEquals(cartman.next_move, (0, -2))


