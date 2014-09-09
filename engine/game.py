#!/usr/bin/env python

from __future__ import division, print_function

import math

import map
import gamestate
import function
import constants

# the main engine class
class Game:
    def __init__(self):
        self.maxplayers = 8
        self.servername = ""
        self.isserver = False

        #DEBUGTOOL
        self.toggle_masks = False
        
        # This list stores all client-made states for interpolating when receiving something from the server
        self.old_client_states = []
        # This list store only the server-corrected ones for rendering
        self.old_server_states = []

        # map data
        self.map_rotation = []
        self.change_map = True

        # game states
        self.current_state = gamestate.Gamestate()

        # A second time counter to make a smooth rendering possible
        self.rendering_time = 0.0

        # This is a hack to allow game objects to append stuff to the networking event queue without having to pass networker around
        self.sendbuffer = []

        # this accumulator is used to update the engine in fixed timesteps
        self.accumulator = 0.0
        #These variables are useful for modifying to change the offsets of objects ingame
        #DEBUGTOOL
        self.horizontal = 0
        self.vertical = 0

    def update(self, networker, frametime):
        if abs(self.rendering_time - self.current_state.time) > 0.5:
            self.rendering_time = self.current_state.time - constants.PHYSICS_TIMESTEP
        self.rendering_time += frametime + frametime*(self.current_state.time+self.accumulator - self.rendering_time)*constants.INTERP_SLIDING_WINDOW
        self.accumulator += frametime

        while self.accumulator >= constants.PHYSICS_TIMESTEP:
            if self.isserver:
                self.accumulator -= constants.PHYSICS_TIMESTEP
                self.current_state.update_all_objects(self, constants.PHYSICS_TIMESTEP)
            else:
                self.old_client_states.append(self.current_state.copy())
                self.accumulator -= constants.PHYSICS_TIMESTEP
                self.current_state.update_all_objects(self, constants.PHYSICS_TIMESTEP)

            for event in self.sendbuffer:
                event.time = self.current_state.time
                networker.sendbuffer.append(event)
            self.sendbuffer = []
