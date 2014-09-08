from __future__ import division, print_function

import struct
import sfml

import function
import networking.databuffer
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
                "up": sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.W),
                "down": sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.S),
                "left": sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.A),
                "right": sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.D)
            }
        
        self.up = self.keys["up"]
        self.down = self.keys["down"]
        self.left = self.keys["left"]
        self.right = self.keys["right"]
        
        self.leftmouse = sfml.window.Mouse.is_button_pressed(sfml.window.Mouse.LEFT)
        self.middlemouse = sfml.window.Mouse.is_button_pressed(sfml.window.Mouse.MIDDLE)
        self.rightmouse = sfml.window.Mouse.is_button_pressed(sfml.window.Mouse.RIGHT)
        
        mouse_x, mouse_y = sfml.window.Mouse.get_position(window)
        self.aimdirection = function.point_direction(window.width / 2, window.height / 2, mouse_x, mouse_y)
        
        inputbuffer = networking.databuffer.Buffer()
        self.serialize_input(inputbuffer)
        event = networking.event_serialize.ClientEventInputstate(inputbuffer)
        game.sendbuffer.append(event)


    def serialize_input(self, packetbuffer):
        keybyte = 0
        
        keybyte |= self.left << 0
        keybyte |= self.right << 1
        keybyte |= self.up << 2
        keybyte |= self.leftmouse << 3
        keybyte |= self.rightmouse << 4
        
        aim = int(round((self.aimdirection % 360) / 360 * 65535))
        
        packetbuffer.write("BH", (keybyte, aim))