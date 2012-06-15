from __future__ import division, print_function

import math
import sfml

import function

class ClassRenderer(object):
    def __init__(self):
        pass

    def render(self, renderer, game, state, character):
        anim_frame = int(character.animoffset)

        if not character.onground(game, state):
            anim_frame = 1

        if character.intel:
            anim_frame += 2

        sprite = self.sprites[anim_frame].copy()

        if character.flip:
            sprite.scale = (-1, 1)
            sprite.origin = self.spriteoffset_flipped
        else:
            sprite.origin = self.spriteoffset

        sprite.position = renderer.get_screen_coords(character.x, character.y)

        renderer.window.draw(sprite)
        #draw mask
        #w, h = character.collision_mask.get_size()
        #location =  renderer.get_screen_coords(character.x, character.y)
        #size = (w,h)
        #color = (153,0,153)
        #pygrafix.draw.rectangle(location,size,color)


class ScoutRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/scoutreds/%i.png" % i))) for i in range(4)]

        self.spriteoffset = (24, 30)
        self.spriteoffset_flipped = (28, 30)

class PyroRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/pyroreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (24, 30)
        self.spriteoffset_flipped = (28, 30)

class SoldierRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/soldierreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (24, 30)
        self.spriteoffset_flipped = (28, 30)

class HeavyRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/heavyreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (14, 30)
        self.spriteoffset_flipped = (36, 30)

class MedicRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/medicreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (23, 30)
        self.spriteoffset_flipped = (29, 30)

class EngineerRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/engineerreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (26, 30)
        self.spriteoffset_flipped = (26, 30)

class SpyRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/spyreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (22, 30)
        self.spriteoffset_flipped = (30, 30)

    def render(self, renderer, game, state, character):
        if not character.cloaking:
            ClassRenderer.render(self, renderer, game, state, character)
            # FIXME: Why is the character still getting drawn on the screen if cloaked?

class QuoteRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture(("characters/quotereds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (16, -1)
        self.spriteoffset_flipped = (16, -1)
