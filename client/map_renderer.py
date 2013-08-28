#!/usr/bin/env python

from __future__ import division, print_function

import sfml
import function

class MapRenderer(object):
    def __init__(self, renderer, mapname):
        self.set_map(mapname)

    def set_map(self, mapname):
        self.bgs = [sfml.Sprite(function.load_texture(("maps/"+ mapname[i] + ".png"))) for i in range(8)]
        for background in self.bgs:
            background.ratio = sfml.system.Vector2(6, 6)
    
    def parallax_map (self, renderer, mapsprites):
        #the list passed to this function are the sprites between the foreground and background
        speed_increment = 1.0/(len(mapsprites)+1)
        for iteration, background in enumerate(mapsprites):
            multiplier = speed_increment * (iteration+1)
            background.position = (-renderer.xview* multiplier, -renderer.yview * ((multiplier + 3.0)/4))
            renderer.window.draw(background)
    
    def render(self, renderer, state):
        #Background (Sky)
        self.bgs[7].position = renderer.get_screen_coords(0, 0)
        renderer.window.draw(self.bgs[7])
        
        #Backgrounds in between
        parallaxed_maps = [self.bgs[i] for i in range(1, 7)]
        parallaxed_maps.reverse()
        self.parallax_map(renderer,parallaxed_maps)
        
        #Foreground
        self.bgs[0].position = renderer.get_screen_coords(0, 0)
        renderer.window.draw(self.bgs[0])
        
    
