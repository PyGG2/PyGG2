from __future__ import division, print_function

import constants
import math
import sfml
import function
import spritefont

class ClassRenderer(object):
    def __init__(self):
        
        pass

    def render(self, renderer, game, state, character):
        anim_frame = int(character.animoffset)

        if not character.onground(game, state):
            anim_frame = 1

        if character.intel:
            anim_frame += 2

        sprite = self.sprites[anim_frame]
        
        if character.flip:
            sprite.ratio = sfml.system.Vector2(-1, 1)
            sprite.origin = self.spriteoffset_flipped
        else:
            sprite.ratio = sfml.system.Vector2(1, 1)
            sprite.origin = self.spriteoffset

        sprite.position = renderer.get_screen_coords(character.x, character.y)

        renderer.window.draw(sprite)
        
        #toggle masks
        if game.toggle_masks:
            rect_location = renderer.get_screen_coords(character.x, character.y)
            
            rect_size= character.collision_mask.get_size()
            rect_mask = sfml.RectangleShape(rect_size)
            
            rect_mask.fill_color = (sfml.Color(255,0,0,125))
            rect_mask.position = (rect_location)
            renderer.window.draw(rect_mask)
        

class ScoutRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/scoutreds/%i.png" % i))) for i in range(4)]

        self.spriteoffset = (24, 30)
        self.spriteoffset_flipped = (35, 30)

class PyroRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/pyroreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (24, 30)
        self.spriteoffset_flipped = (35, 30)

class SoldierRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/soldierreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (24, 30)
        self.spriteoffset_flipped = (35, 30)

class HeavyRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/heavyreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (14, 30)
        self.spriteoffset_flipped = (26, 30)

class MedicRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/medicreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (23, 30)
        self.spriteoffset_flipped = (36, 30)

class EngineerRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/engineerreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (26, 30)
        self.spriteoffset_flipped = (36, 30)

class SpyRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/spyreds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (22, 30)
        self.spriteoffset_flipped = (33, 30)

    def render(self, renderer, game, state, character):
        if not character.cloaking:
            ClassRenderer.render(self, renderer, game, state, character)
            # FIXME: Why is the character still getting drawn on the screen if cloaked?

class QuoteRenderer(ClassRenderer):
    def __init__(self):
        self.depth = 0
        self.sprites = [sfml.Sprite(function.load_texture((constants.SPRITE_FOLDER + "characters/quotereds/%s.png" % i))) for i in range(4)]

        self.spriteoffset = (16, -1)
        self.spriteoffset_flipped = (16, -1)
