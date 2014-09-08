from __future__ import division, print_function

import math
import sfml
import random

import function
import spritefont
import constants

class BuildingSentryRenderer(object):
    def __init__(self):
        self.depth = -1
        self.sprites = [sfml.graphics.Sprite(function.load_texture(constants.SPRITE_FOLDER + "ingameelements/sentryred/{0}.png".format(i))) for i in range(10)]

    def render(self, renderer, game, state, sentry):
        sprite_offset_flipped = (-12,-20)
        sprite_offset = (-8,-20)
        sprite = self.sprites[min(int(sentry.animation_frame), 9)] # TODO, get rid of this min and figure out how to cap an image index

        if sentry.flip == True:
            sprite.ratio = sfml.system.Vector2(-1, 1)
            sprite.position = renderer.get_screen_coords(sentry.x + sprite_offset_flipped[0], sentry.y + sprite_offset_flipped[1])
        else:
            sprite.ratio = sfml.system.Vector2(1, 1)
            sprite.position = renderer.get_screen_coords(sentry.x + sprite_offset[0] , sentry.y + sprite_offset[1] )


        renderer.window.draw(sprite)

        ##draw mask
        #w, h = sentry.collision_mask.get_size()
        #location =  renderer.get_screen_coords(sentry.x, sentry.y)
        #size = (w,h)
        #color = (153,0,153)
        #pygrafix.draw.rectangle(location,size,color)

class SentryRenderer(object):
    def __init__(self):
        self.depth = -1
        self.base = sfml.graphics.Sprite(function.load_texture(constants.SPRITE_FOLDER + "ingameelements/sentryred/11.png"))
        self.turrets = [sfml.graphics.Sprite(function.load_texture(constants.SPRITE_FOLDER + "ingameelements/sentryturrets/{0}.png".format(i))) for i in range(3)]
        self.turning = [sfml.graphics.Sprite(function.load_texture(constants.SPRITE_FOLDER + "ingameelements/turretrotates/{0}.png".format(i))) for i in range(5)]

    def render(self, renderer, game, state, sentry):
        basesprite_offset = (-8,-20)
        basesprite_flipped = (-12,-20)

        turretsprite_offset = (13,4)
        turretsprite_flipped = (14,6)

        basesprite = self.base

        if sentry.rotating == False:
            turretsprite = self.turrets[0]
        else:
            turretsprite = self.turning[int(round(sentry.rotateindex))]

        turretsprite_rotate_point = (18,8)
        turretsprite_rotate_flipped = (16,8)

        if sentry.flip == True:
            basesprite.ratio = (-1, 1)
            basesprite.position = renderer.get_screen_coords(sentry.x + basesprite_flipped[0], sentry.y + basesprite_flipped[1])
        else:
            basesprite.ratio = (1, 1)
            basesprite.position = renderer.get_screen_coords(sentry.x + basesprite_offset[0], sentry.y + basesprite_offset[1])

        if sentry.rotating == False:
            if sentry.turret_flip == sentry.flip:
                if sentry.flip == False:
                    turretsprite.ratio = (1-2*sentry.flip, -1)# x == -1 if sentry.flip, == 1 if not
                    turretsprite.position = renderer.get_screen_coords(sentry.x + turretsprite_offset[0],sentry.y + turretsprite_offset[1])
                    turretsprite_rotate = (turretsprite_rotate_point[0] , turretsprite_rotate_point[1])
                else:
                    turretsprite.ratio = (1-2*sentry.flip, 1)# x == -1 if sentry.flip, == 1 if not
                    turretsprite.position = renderer.get_screen_coords(sentry.x + turretsprite_flipped[0],sentry.y + turretsprite_flipped[1])
                    turretsprite_rotate = (turretsprite_rotate_flipped[0] , turretsprite_rotate_flipped[1])
            else:
                # if the sentry head is facing the opposite direction to its original position
                if sentry.flip == False:
                    turretsprite.ratio = (1-2*sentry.flip, -1)# x == -1 if sentry.flip, == 1 if not
                    turretsprite.position = renderer.get_screen_coords(sentry.x + turretsprite_flipped[0],sentry.y + turretsprite_flipped[1])
                    turretsprite_rotate = (turretsprite_rotate_flipped[0] , turretsprite_rotate_flipped[1])
                else:
                    turretsprite.ratio = (1-2*sentry.flip, 1)# x == -1 if sentry.flip, == 1 if not
                    turretsprite.position = renderer.get_screen_coords(sentry.x + turretsprite_offset[0],sentry.y + turretsprite_offset[1])
                    turretsprite_rotate = (turretsprite_rotate_point[0] , turretsprite_rotate_point[1])
            #if the sentry is not rotating, put in the anchor
            turretsprite.origin = turretsprite_rotate
            turretsprite.rotation = 360 - sentry.direction
        else:
            #sentry is rotating, ignore anchor
            #TODO: make animation play backwards
            turretsprite.ratio = (1-2*sentry.flip, 1)# x == -1 if sentry.flip, == 1 if not
            turretsprite.position = renderer.get_screen_coords(sentry.x,sentry.y)

        #debugpoint = renderer.get_screen_coords(sentry.x + game.horizontal, sentry.y +  game.vertical)


        renderer.window.draw(basesprite)
        renderer.window.draw(turretsprite) #Turret overlays, so goes second
