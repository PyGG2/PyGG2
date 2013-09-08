from __future__ import division, print_function

import math
import sfml
import random

import function
import constants

class ShotRenderer(object):
    def __init__(self):
        self.depth = 1
        self.shotsprite = sfml.Sprite(function.load_texture(constants.SPRITE_FOLDER + "projectiles/shots/0.png"))

    def render(self, renderer, game, state, shot):
        if shot.flight_time < 0:
            return
        
        sprite = self.shotsprite
        sprite.rotation = 360 - shot.direction

        if shot.max_flight_time - shot.flight_time < shot.fade_time:
            sprite.color.a = 255*(shot.max_flight_time - shot.flight_time) / shot.fade_time

        sprite.position = renderer.get_screen_coords(shot.x, shot.y)

        renderer.window.draw(sprite)


class FlameRenderer(object):
    def __init__(self):
        self.depth = 1
        self.currentindex = -1
        self.flamesprite = [sfml.Sprite(function.load_texture(constants.SPRITE_FOLDER + "projectiles/flames/{}.png".format(i))) for i in range(3)]

    def render(self, renderer, game, state, flame):
        if flame.flight_time < 0:
            return

        #sprite animation
        if self.currentindex == -1:
            self.currentindex = 0
        else:
            if self.currentindex == 2:
                self.currentindex = 0
            else:
                self.currentindex += 1

        sprite = self.flamesprite[self.currentindex]

        sprite.position = renderer.get_screen_coords(flame.x,flame.y)

        renderer.window.draw(sprite)

class RocketRenderer(object):
    def __init__(self):
        self.depth = 1
        self.rocketsprite = sfml.Sprite(function.load_texture(constants.SPRITE_FOLDER + "projectiles/rockets/0.png"))

    def render(self, renderer, game, state, rocket):
        if rocket.flight_time < 0:
            return

        sprite = self.rocketsprite
        sprite.rotation = 360 - rocket.direction

        sprite.color.a = min((rocket.max_flight_time - rocket.flight_time) / rocket.fade_time, 1)

        sprite.position = renderer.get_screen_coords(rocket.x, rocket.y)

        renderer.window.draw(sprite)

class MineRenderer(object):
    def __init__(self):
        self.depth = 1
        self.minesprite = sfml.Sprite(function.load_texture(constants.SPRITE_FOLDER + "projectiles/mines/1.png"))

    def render(self, renderer, game, state, mine):
        if mine.flight_time < 0:
            return

        sprite = self.minesprite
        sprite.rotation = 360 - mine.direction

        sprite.position = renderer.get_screen_coords(mine.x, mine.y)

        renderer.window.draw(sprite)

class NeedleRenderer(object):
    def __init__(self):
        self.depth = 1
        self.needlesprite = sfml.Sprite(function.load_texture(constants.SPRITE_FOLDER + "projectiles/needles/0.png"))

    def render(self, renderer, game, state, needle):
        if needle.flight_time < 0:
            return

        sprite = self.needlesprite
        sprite.rotation = 360 - needle.direction

        if needle.max_flight_time - needle.flight_time < needle.fade_time:
            sprite.color.a = (needle.max_flight_time - needle.flight_time) / needle.fade_time

        sprite.position = renderer.get_screen_coords(needle.x, needle.y)

        renderer.window.draw(sprite)

class BladeRenderer(object):
    def __init__(self):
        self.depth = 1
        self.bladesprite = sfml.Sprite(function.load_texture(constants.SPRITE_FOLDER + "projectiles/bladeprojectiles/0.png"))

    def render(self, renderer, game, state, blade):
        if blade.flight_time < 0:
            return

        sprite = self.bladesprite
        sprite.rotation = 360 - blade.direction

        sprite.position = renderer.get_screen_coords(blade.x, blade.y)

        renderer.window.draw(sprite)
