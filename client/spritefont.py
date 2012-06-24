from __future__ import division

#import pygrafix
import function
import sfml


class SpriteFont(object):
    def __init__(self, bold=False):
        if bold:
            self.texture = sfml.Texture.load_from_file('sprites/fontbold.png')
            self.cw = 9
            self.ch = 13
        else:
            self.texture = sfml.Texture.load_from_file('sprites/font.png')
            self.cw = 7
            self.ch = 13
        #self.chars = list([self.texture.get_region((char % 16) * self.cw, (char // 16) * self.ch, self.cw, self.ch) for char in range(256)])
        #self.chars = list([self.texture.get_region((char % 16) * self.cw, (char // 16) * self.ch, self.cw, self.ch) for char in range(256)])
        self.chars = []
        sprite = sfml.Sprite(self.texture)
        for char in range(256):
            #Create a sfml sprite object for each letter
            #sprite.texture_rect = sfml.IntRect((char % 16) * self.cw, (char // 16) * self.ch, self.cw, self.ch)
            sprite.set_texture_rect(sfml.IntRect((char % 16) * self.cw, (char // 16) * self.ch, self.cw, self.ch))
            self.chars.append(sprite.copy())

    def stringSize(self, string):
        return (len(string) * self.cw, self.ch)
            
    def renderString(self, string, x, y, renderer):
        sprites = []
        for i, char in enumerate(string):
            char = ord(char)
            if char > 255: # too big to be in font
                char = ord(' ')
            sprite = (self.chars[char])
            sprite.position = (12 + i*self.cw,10)
            renderer.window.draw(sprite)
            #sprites.append(sprite)
        #pygrafix.sprite.draw_batch(sprites, scale_smoothing = False, blending = 'add')
