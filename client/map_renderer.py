#!/usr/bin/env python

from __future__ import division, print_function

import sfml
import function

class MapRenderer(object):
    def __init__(self, renderer, mapname):
        self.set_map(mapname)

    def set_map(self, mapname):
        self.sprite = sfml.Sprite(function.load_texture("maps/" + mapname + ".png"))
        self.sprite.scale(6, 6)

    def render(self, renderer, state):
        self.sprite.position = (-renderer.xview, -renderer.yview)
        renderer.window.draw(self.sprite)
