from __future__ import division, print_function

import math
import pygrafix
import random

import function

class BuildingSentryRenderer(object):
    def __init__(self):
        self.depth = -1
        self.sprites = list([pygrafix.image.load("sprites/ingameelements/sentryred/{0}.png".format(i)) for i in range(10)])
        
    def render(self, renderer, game, state, sentry):
        sprite_offset_flipped = (-12,-20)
        sprite_offset = (-8,-20)
        self.sprite = self.sprites[min(int(sentry.animation_frame), 9)] # TODO, get rid of this min and figure out how to cap an image index
        sprite = pygrafix.sprite.Sprite(self.sprite)
        
        if sentry.flip == True:
            sprite.flip_x = True
            sprite.position = renderer.get_screen_coords(sentry.x + sprite_offset_flipped[0], sentry.y + sprite_offset_flipped[1])
        else:
            sentry.flip_x = False
            sprite.position = renderer.get_screen_coords(sentry.x + sprite_offset[0] , sentry.y + sprite_offset[1] )
        

        renderer.world_sprites.append(sprite)
        
        ##draw mask
        #w, h = sentry.collision_mask.get_size()
        #location =  renderer.get_screen_coords(sentry.x, sentry.y)
        #size = (w,h)
        #color = (153,0,153)
        #pygrafix.draw.rectangle(location,size,color)
        
class SentryRenderer(object):
    def __init__(self):
        self.depth = -1
        self.base = pygrafix.image.load("sprites/ingameelements/sentryred/11.png")
        self.turrets = list([pygrafix.image.load("sprites/ingameelements/sentryturrets/{0}.png".format(i)) for i in range(3)])
        
    def render(self, renderer, game, state, sentry):
        basesprite_offset = (-8,-20)
        basesprite_flipped = (-12,-20)
        
        turretsprite_offset = (13,4)
        turretsprite_flipped = (14,6)
        
        basesprite = self.base
        basesprite = pygrafix.sprite.Sprite(basesprite)
    
        turretsprite = self.turrets[0]
        turretsprite = pygrafix.sprite.Sprite(turretsprite)
        
        turretsprite_rotate_point = (18,8)
        turretsprite_rotate_flipped = (16,8)
        debugpoint = (0,0)
        
        if sentry.flip == True:
            basesprite.flip_x = True
            turretsprite.flip_y = True
            basesprite.position = renderer.get_screen_coords(sentry.x + basesprite_flipped[0], sentry.y + basesprite_flipped[1])
            turretsprite.position = renderer.get_screen_coords(sentry.x + turretsprite_flipped[0],sentry.y + turretsprite_flipped[1])
            turretsprite_rotate = (turretsprite_rotate_flipped[0] , turretsprite_rotate_flipped[1])
            #debugpoint = renderer.get_screen_coords(sentry.x + turretsprite_rotate_flipped[0],sentry.y + turretsprite_rotate_flipped[1])
        else:
            basesprite.flip_x = False
            turretsprite.flip_y = False
            basesprite.position = renderer.get_screen_coords(sentry.x + basesprite_offset[0], sentry.y + basesprite_offset[1])
            turretsprite.position = renderer.get_screen_coords(sentry.x + turretsprite_offset[0],sentry.y + turretsprite_offset[1])
            turretsprite_rotate = (turretsprite_rotate_point[0] , turretsprite_rotate_point[1])
            #debugpoint = renderer.get_screen_coords(sentry.x + turretsprite_rotate_point[0], sentry.y + turretsprite_rotate_point[1])
        
        turretsprite.anchor = turretsprite_rotate
        turretsprite.rotation = 360 - sentry.direction
        
        renderer.world_sprites.append(turretsprite)
        renderer.world_sprites.append(basesprite)
        
        ##draw mask
        #w, h = sentry.collision_mask.get_size()
        #location =  renderer.get_screen_coords(sentry.x, sentry.y)
        #size = (w,h)
        #color = (153,0,153)
        #pygrafix.draw.rectangle(location,size,color)
        
        #draw alignment point
        #self.debugpointbar = DebugRotatePoint()
        #self.debugpointbar.debugpoint = debugpoint
        #renderer.hud_overlay.append(self.debugpointbar)
class DebugRotatePoint(object):
    def render(self):
        pygrafix.draw.rectangle(self.debugpoint,(1,1),(0,0,1))