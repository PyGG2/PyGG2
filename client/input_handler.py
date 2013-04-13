from __future__ import division, print_function

import struct
import sfml

import function
import networking.event_serialize

class InputHandler(object):
    def __init__(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.leftmouse = False
        self.middlemouse = False
        self.rightmouse = False
        self.aimdirection = 0
        
        self.keys = {}
        self.oldkeys = {}
    
    def gather_input(self, window, game):
        self.keys = {
                "up": sfml.Keyboard.is_key_pressed(sfml.Keyboard.W),
                "down": sfml.Keyboard.is_key_pressed(sfml.Keyboard.S),
                "left": sfml.Keyboard.is_key_pressed(sfml.Keyboard.A),
                "right": sfml.Keyboard.is_key_pressed(sfml.Keyboard.D)
            }
        
        self.up = self.keys["up"]
        self.down = self.keys["down"]
        self.left = self.keys["left"]
        self.right = self.keys["right"]
        
        self.leftmouse = sfml.Mouse.is_button_pressed(sfml.Mouse.LEFT)
        self.middlemouse = sfml.Mouse.is_button_pressed(sfml.Mouse.MIDDLE)
        self.rightmouse = sfml.Mouse.is_button_pressed(sfml.Mouse.RIGHT)
        
        mouse_x, mouse_y = sfml.Mouse.get_position(window)
        self.aimdirection = function.point_direction(window.width / 2, window.height / 2, mouse_x, mouse_y)
        
        bytestr = self.serialize_input()
        event = networking.event_serialize.ClientEventInputstate(bytestr)
        game.sendbuffer.append(event)


    def serialize_input(self):
        keybyte = 0
        
        keybyte |= self.left << 0
        keybyte |= self.right << 1
        keybyte |= self.up << 2
        keybyte |= self.leftmouse << 3
        keybyte |= self.rightmouse << 4
        
        aim = int(round((self.aimdirection % 360) / 360 * 65535))
        
        bytestr = struct.pack(">BH", keybyte, aim)
        
        return bytestr