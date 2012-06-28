from __future__ import division, print_function

import math

import function
import spritefont
import sfml

class HudRenderer(object):
    
    def render(self, renderer, game, state):

        self.hudsprite.position = self.sprite_location
        self.hudsprite.scale = (2,2)
        renderer.hud_sprites.append (self.hudsprite)
        
class HealthRenderer(HudRenderer):

    def __init__(self, renderer, game, state, character_id):

        self.sprite_location = (10, renderer.view_height - 75)
        character = state.entities[character_id]
        my_class_type = type(character)
        my_class_number = str(function.convert_class(my_class_type))
       
        self.hudsprite = sfml.Sprite(function.load_texture("huds/characterhud/"+ my_class_number + ".png"))

        self.health_box_background = None
        self.health_box = None

        self.health_text = HealthText()
        self.health_text.health_location = (56, renderer.view_height - 52)
        self.health_text.health_size = (36, 36)
        
    def render(self, renderer, game, state, character_id):
        super(HealthRenderer,self).render(renderer, game, state)
        
        character = state.entities[character_id]
        character_hp = int(character.hp)
        
        character_maxhp = character.maxhp
        #always have at least 1 percent, can't divide by zero!
        health_percentage = max(0.01,(character_hp / character_maxhp))
       
        self.health_text.text = str(character_hp)
        
        #The black background behind green health
        self.health_box_background = DrawRectangle() 
        self.health_box_background.location = (52, (renderer.view_height - 53))
        self.health_box_background.size = (40, 39)
        self.health_box_background.color = (sfml.Color.BLACK)
        renderer.hud_overlay.append(self.health_box_background)
        
        #The Green Health
        self.health_box = DrawRectangle()
        self.health_box.location = (52, min ( (renderer.view_height - 12), (renderer.view_height - 53) + (39 - 39 * abs(health_percentage))) )
        self.health_box.size = (40, max(0, 39 * health_percentage))

        if health_percentage > 0.5:
            exponent = 2 # The higher this will be, the quicker will the change happen, and the flatter will the curve be
            # Color it green-yellow
            self.health_box.color = sfml.Color(((1 - 2*(health_percentage-0.5))**exponent)*220, 220, 0, 255)
        else:
            exponent = 3 # The higher this will be, the quicker will the change happen, and the flatter will the curve be
            # Color it yellow-red
            self.health_box.color = sfml.Color(255, ((2*health_percentage)**exponent)*255, 0, 255)
        renderer.hud_overlay.append(self.health_box)
        renderer.hud_overlay.append(self.health_text)

class DrawRectangle(object):
    def render(self, renderer, game, state):
        
        rect = sfml.RectangleShape(self.size)
        rect.fill_color = self.color
        rect.position = (self.location)
        renderer.window.draw(rect)

class HealthText(object):
    def __init__(self):
        self.font = spritefont.SpriteFont(bold=True)
        
    def render(self, renderer, game, state):
        tw, th = self.font.stringSize(self.text)
        tx = self.health_location[0] + (self.health_size[0] - tw)/2
        ty = self.health_location[1] + (self.health_size[1] - th)/2
        self.font.renderString(self.text, renderer.window, tx, ty, )

