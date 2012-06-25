from __future__ import division

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
        self.chars = []
        sprite = sfml.Sprite(self.texture)
        for char in range(256):
            #Create a sfml sprite object for each letter
            r = sfml.IntRect((char % 16) * self.cw, (char // 16) * self.ch, self.cw, self.ch)
            try:
                sprite.set_texture_rect(r)
            except AttributeError:
                sprite.texture_rect = r
            self.chars.append(sprite.copy())

    def stringSize(self, string):
        return (len(string) * self.cw, self.ch)
            
    def renderString(self, string, renderer, x, y):

        for i, char in enumerate(string):
            char = ord(char)
            if char > 255: # too big to be in font
                char = ord(' ')
            text = (self.chars[char])
            text.position = (x + i*self.cw,y)
            renderer.window.draw(text)
