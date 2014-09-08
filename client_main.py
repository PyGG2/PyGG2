#!/usr/bin/env python

from client.handler import ClientManager
from client.main import GameClientHandler
from client.menus import MainMenuHandler

# DEBUG ONLY
import cProfile
import pstats
import os

def profileGG2():
    cProfile.run("GG2main()", sort="time")

def GG2main(skipmenu=False):
    if skipmenu:
        cm = ClientManager(GameClientHandler)
    else:
        cm = ClientManager(MainMenuHandler)
    cm.run()

if __name__ == "__main__":
    # when profiling:
    profileGG2()
    # GG2main()
