import Pyro4
from engine import *
import logging
import sys

# Board Size
N = 10
M = 13 


if __name__ == '__main__':
    #instantiate game engine and run pyro daemon
    game = Engine(N, M)
    game.run()
    Pyro4.Daemon.serveSimple(
            {
                game: "server.game"
            },
            ns = False)
