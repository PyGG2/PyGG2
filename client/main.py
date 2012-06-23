import precision_timer
import sfml

from .handler import Handler
from . import networker, rendering, spectator
import function
import engine.game, engine.player
import constants
import networking
import random
def get_input(window):
    return {
        "up": sfml.Keyboard.is_key_pressed(sfml.Keyboard.W),
        "down": sfml.Keyboard.is_key_pressed(sfml.Keyboard.S),
        "left": sfml.Keyboard.is_key_pressed(sfml.Keyboard.A),
        "right": sfml.Keyboard.is_key_pressed(sfml.Keyboard.D)
    }

# handler for when client is in game
class GameClientHandler(Handler):
    def __init__(self, window, manager):
        self.manager = manager
        self.window = window

        # create game engine object
        self.game = engine.game.Game()

        self.server_password = ""# FIXME: Remove and replace with something more flexible
        self.player_name = str(self.manager.config.setdefault('player_name', 'nightcracker'))
        self.server_ip = str(self.manager.config.setdefault('server_ip', '127.0.0.1'))
        self.server_port = str(self.manager.config.setdefault('server_port', 8190))
        # Create the networking-handler
        self.networker = networker.Networker((self.server_ip, int(self.server_port)), self) # FIXME: Remove these values, and replace with something easier.
        self.network_update_timer = 0

        # Gets set to true when we're disconnecting, for the networker
        self.destroy = False

        #Generate Dictionary
        self.pressed_dict = {}

        #Whether or not the window is focused
        self.window_focused = True


    def start_game(self, player_id):
        # Only start the game once the networker has confirmed a connection with the server

        # keep state of keys stored for one frame so we can detect down/up events
        self.keys = get_input(self.window)
        self.oldkeys = self.keys

        # TODO REMOVE THIS
        # create player
        self.our_player_id = engine.player.Player(self.game, self.game.current_state, player_id).id
        self.spectator = spectator.Spectator(self.our_player_id)

        # create renderer object
        self.renderer = rendering.GameRenderer(self)

        # pygame time tracking
        self.clock = precision_timer.Clock()
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
                if not self.window.open or running == False:
                    self.window.close()
                    break
                leftmouse = False
                #main input handling loop
                for event in self.window.iter_events():
                    if event.type == sfml.Event.CLOSED: #Press the 'x' button
                        running = False
                    elif event.type == sfml.Event.LOST_FOCUS:
                        self.window_focused = False
                    elif event.type == sfml.Event.GAINED_FOCUS:
                        self.window_focused = True
                    elif event.type == sfml.Event.KEY_PRESSED: #Key handler
                        if event.code == sfml.Keyboard.ESCAPE:
                            running = False
                        elif event.code == sfml.Keyboard.LEFT:
                                self.game.horizontal -= 1
                        elif event.code == sfml.Keyboard.RIGHT:
                            self.game.horizontal += 1
                        elif event.code == sfml.Keyboard.UP:
                            self.game.vertical -= 1
                        elif event.code == sfml.Keyboard.DOWN:
                            self.game.vertical += 1
                        elif event.code == sfml.Keyboard.L_SHIFT:
                            print("HORIZONTAL OFFSET = " + str(self.game.horizontal))
                            print("VERTICAL OFFSET = " + str(self.game.vertical))

                # handle input if window is focused
                self.oldkeys = self.keys
                self.keys = get_input(self.window)
                if self.window_focused:
                    leftmouse = sfml.Mouse.is_button_pressed(sfml.Mouse.LEFT)
                    middlemouse = sfml.Mouse.is_button_pressed(sfml.Mouse.MIDDLE)
                    rightmouse = sfml.Mouse.is_button_pressed(sfml.Mouse.RIGHT)

                    mouse_x, mouse_y = sfml.Mouse.get_position(self.window)
                    our_player = self.game.current_state.players[self.our_player_id]
                    our_player.up = self.keys["up"]
                    our_player.down = self.keys["down"]
                    our_player.left = self.keys["left"]
                    our_player.right = self.keys["right"]
                    our_player.leftmouse = leftmouse
                    our_player.middlemouse = middlemouse
                    our_player.rightmouse = rightmouse
                    our_player.aimdirection = function.point_direction(self.window.width / 2, self.window.height / 2, mouse_x, mouse_y)

                    if sfml.Keyboard.is_key_pressed(sfml.Keyboard.NUM1):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_SCOUT)
                        self.networker.events.append((self.networker.sequence, event))
                    elif sfml.Keyboard.is_key_pressed(sfml.Keyboard.NUM2):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_PYRO)
                        self.networker.events.append((self.networker.sequence, event))
                    elif sfml.Keyboard.is_key_pressed(sfml.Keyboard.NUM3):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_SOLDIER)
                        self.networker.events.append((self.networker.sequence, event))
                    elif sfml.Keyboard.is_key_pressed(sfml.Keyboard.NUM4):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_HEAVY)
                        self.networker.events.append((self.networker.sequence, event))
                    elif sfml.Keyboard.is_key_pressed(sfml.Keyboard.NUM6):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_MEDIC)
                        self.networker.events.append((self.networker.sequence, event))
                    elif sfml.Keyboard.is_key_pressed(sfml.Keyboard.NUM7):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_ENGINEER)
                        self.networker.events.append((self.networker.sequence, event))
                    elif sfml.Keyboard.is_key_pressed(sfml.Keyboard.NUM8):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_SPY)
                        self.networker.events.append((self.networker.sequence, event))
                    elif sfml.Keyboard.is_key_pressed(sfml.Keyboard.Q):
                        event = networking.event_serialize.ClientEventChangeclass(constants.CLASS_QUOTE)
                        self.networker.events.append((self.networker.sequence, event))

                    # did we just release the F11 button? if yes, go fullscreen
                    #if sfml.Keyboard.is_key_pressed(sfml.Keyboard.F11):
                    #    self.window.fullscreen = not self.window.fullscreen

                # update the game and render
                frame_time = self.clock.tick()
                frame_time = min(0.25, frame_time) # a limit of 0.25 seconds to prevent complete breakdown

                self.fpscounter_accumulator += frame_time

                self.networker.recieve(self.game, self)
                self.game.update(self.networker, frame_time)
                self.renderer.render(self, self.game, frame_time)

                if self.network_update_timer >= constants.INPUT_SEND_FPS:
                    self.networker.update(self)
                    self.network_update_timer = 0
                else:
                    self.network_update_timer += frame_time

                if self.fpscounter_accumulator > 1.0:
                    self.window.title = "PyGG2 - %d FPS" % (self.fpscounter_frames / self.fpscounter_accumulator)
                    self.fpscounter_accumulator = 0.0
                    self.fpscounter_frames = 0

                self.window.display()
                self.fpscounter_frames += 1
        self.cleanup()

    def cleanup(self):
        #clear buffer, send disconnect, and kiss and fly
        event = networking.event_serialize.ClientEventDisconnect()
        self.networker.sendbuffer.append(event)
        self.destroy = True #set flag to networker.update that we are destroying
        self.networker.update(self)
