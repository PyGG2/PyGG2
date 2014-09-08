from __future__ import division, print_function

import precision_timer
import sfml

from .handler import Handler
from . import networker, rendering, spectator
import function
import engine.game, engine.player
import constants
import networking
import time
import input_handler

# handler for when client is in game
class GameClientHandler(Handler):
    def __init__(self, window, manager, host=None, port=None):
        self.manager = manager
        self.window = window

        # create game engine object
        self.game = engine.game.Game()

        self.server_password = ""# FIXME: Remove and replace with something more flexible
        self.player_name = str(self.manager.config.setdefault('player_name', 'Tenderfoot'))
        
        if host and port:
            self.server_ip = host
            self.server_port = port
        else:
            self.server_ip = str(self.manager.config.setdefault('server_ip', '127.0.0.1'))
            self.server_port = str(self.manager.config.setdefault('server_port', 8190))
        print("Trying to connect to " + str(self.server_ip) + " at port: " + str(self.server_port))

        # Create the networking-handler
        self.networker = networker.Networker((self.server_ip, int(self.server_port)), self) # FIXME: Remove these values, and replace with something easier.
        self.network_update_timer = 0

        # Gets set to true when we're disconnecting, for the networker
        self.destroy = False

        #Generate Dictionary
        self.pressed_dict = {}

        #Whether or not the window is focused
        self.window_focused = True
        
        #precision time tracker
        self.clock = precision_timer.Clock()
        
        self.timeout_accumulator = 0.0
    def start_game(self, player_id, state):
        # Only start the game once the networker has confirmed a connection with the server

        # TODO REMOVE THIS
        # create player
        self.our_player_id = engine.player.Player(self.game, state, player_id).id
        self.spectator = spectator.Spectator(self.our_player_id)

        # create renderer object
        self.renderer = rendering.GameRenderer(self)

        # create input handler
        self.input_handler = input_handler.InputHandler()

        # Time tracking
        self.inputsender_accumulator = 0.0 # this counter will accumulate time to send input at a constant rate
        self.fpscounter_accumulator = 0.0 # this counter will tell us when to update the fps info in the title
        self.fpscounter_frames = 0 # this counter will count the number of frames there are before updating the fps info

    def step(self):
        #game loop
        running = True
        while True:
            self.networker.recieve(self.game, self)
            if self.networker.has_connected:
                # check if user exited the game
                if not self.window.is_open or running == False:
                    self.window.close()
                    break
                leftmouse = False
                #main input handling loop
                for event in self.window.events:
                    if isinstance(event, sfml.window.CloseEvent):#Press the 'x' button
                        running = False
                    elif isinstance(event, sfml.window.FocusEvent):
                        self.window_focused = event.gained
                    elif isinstance(event, sfml.window.KeyEvent): #Key handler
                        if event.code == sfml.window.Keyboard.ESCAPE:
                            running = False
                        elif event.code == sfml.window.Keyboard.LEFT:
                            self.game.horizontal -= 1
                        elif event.code == sfml.window.Keyboard.RIGHT:
                            self.game.horizontal += 1
                        elif event.code == sfml.window.Keyboard.UP:
                            self.game.vertical -= 1
                        elif event.code == sfml.window.Keyboard.DOWN:
                            self.game.vertical += 1
                        elif event.code == sfml.window.Keyboard.L_SHIFT:
                            print("HORIZONTAL OFFSET = " + str(self.game.horizontal))
                            print("VERTICAL OFFSET = " + str(self.game.vertical))

                # handle input if window is focused
                if self.window_focused:
                    if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM1):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_SCOUT)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM2):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_PYRO)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM3):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_SOLDIER)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM4):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_HEAVY)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM5):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_DEMOMAN)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM6):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_MEDIC)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM7):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_ENGINEER)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.NUM8):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_SPY)
                        self.game.sendbuffer.append(event)
                    elif sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.Q):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_QUOTE)
                        self.game.sendbuffer.append(event)

                    # did we just release the F11 button? if yes, go fullscreen
                    #if sfml.window.Keyboard.is_key_pressed(sfml.window.Keyboard.F11):
                    #    self.window.fullscreen = not self.window.fullscreen

                # update the game and render
                frametime = self.clock.tick()
                frametime = min(0.25, frametime) # a limit of 0.25 seconds to prevent complete breakdown

                self.fpscounter_accumulator += frametime
                
                self.networker.recieve(self.game, self)
                self.input_handler.gather_input(self.window, self.game)
                self.game.update(self.networker, frametime)
                self.renderer.render(self, self.game, frametime)

                if self.network_update_timer >= constants.INPUT_SEND_FPS:
                    self.networker.update(self)
                    self.network_update_timer = 0
                else:
                    self.network_update_timer += frametime

                if self.fpscounter_accumulator > 1.0:
                    #self.window.title = "PyGG2 - %d FPS" % (self.fpscounter_frames / self.fpscounter_accumulator)
                    self.fpscounter_accumulator = 0.0
                    self.fpscounter_frames = 0

                self.window.display()
                self.fpscounter_frames += 1
            else:
                frametime = self.clock.tick()
                frametime = min(0.25, frametime)
                self.timeout_accumulator += frametime
                if not self.window.is_open:
                    self.window.close()
                    return (False)
                # We still need to poll the window to keep it responding
                for event in self.window.events:
                    if isinstance(event, sfml.window.CloseEvent): #Press the 'x' button
                        return (False)
                    elif isinstance(event, sfml.window.KeyEvent): #Key handler
                        if event.code == sfml.window.Keyboard.ESCAPE:
                            return (False)
                # TODO: writing to title currently crashes pysfml - will get fixed very soon
                #self.window.title = "PyGG2 - Not Connected %dsecs" % (self.timeout_accumulator)
                #Finally, if the server is not reachable, end everything.
                if self.timeout_accumulator > constants.CONNECTION_TIMEOUT:
                    print("Unable to connect to " + str(self.server_ip) + " at port: " + str(self.server_port))
                    return (False) #exit
                time.sleep(max(frametime, 0.25)) # Slow down the execution rate
        self.cleanup()

    def cleanup(self):
        #clear buffer, send disconnect, and kiss and fly
        event = networking.event_serialize.ClientEventDisconnect()
        self.networker.sendbuffer.append(event)
        self.destroy = True #set flag to networker.update that we are destroying
        self.networker.update(self)
