from __future__ import division

import function
import sfml
import constants

class SpriteFont(object):
    def __init__(self, bold=False):
        if bold:
            self.texture = sfml.graphics.Texture.from_file(constants.SPRITE_FOLDER + 'fontbold.png')
            self.cw = 9
            self.ch = 13
        else:
            self.texture = sfml.graphics.Texture.from_file(constants.SPRITE_FOLDER + 'font.png')
            self.cw = 7
            self.ch = 13
        self.chars = []
        for char in range(256):
            #Create a sfml sprite object for each letter
            sprite = sfml.graphics.Sprite(self.texture)
            r = sfml.graphics.Rectangle(((char % 16) * self.cw, (char // 16) * self.ch), (self.cw, self.ch))
            sprite.texture_rectangle = r
            self.chars.append(sprite)

    def stringSize(self, string):
        return (len(string) * self.cw, self.ch)
            
    def renderString(self, string, window, x, y):
        for i, char in enumerate(string):
            char = ord(char)
            if char > 255: # too big to be in font
                char = ord(' ')
            text = (self.chars[char])
            text.position = (x + i*self.cw,y)
            window.draw(text)
