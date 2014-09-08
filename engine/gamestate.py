#!/usr/bin/env python

from __future__ import division, print_function

import map
import networking.event_serialize

# the main physics class
# contains the complete game state
class Gamestate(object):
    def __init__(self):
        self.entities = {}
        self.players = {}
        self.next_entity_id = 0
        self.time = 0.0
        self.map = None

    def update_all_objects(self, game, frametime):
        # time is synced with 4 bytes, so to force looping one would have to host for a straight two years...
        self.time += frametime
        self.time = round(self.time, 6)

        if game.change_map and game.isserver:
            next_map = game.map_rotation.pop()
            print(next_map)
            self.map = map.Map(game, next_map)
            game.map_rotation.append(next_map)
            
            game.sendbuffer.append(networking.event_serialize.ServerChangeMap(next_map))
            
            game.change_map = False

        for entity in self.entities.values(): entity.beginstep(game, self, frametime)
        for player in self.players.values(): player.step(game, self, frametime)
        for entity in self.entities.values(): entity.step(game, self, frametime)
        for entity in self.entities.values(): entity.endstep(game, self, frametime)

    #def update_synced_objects(self, game, frametime):
    #    for entity in self.entities.values():
    #        if entity.issynced:
    #            entity.beginstep(game, self, frametime)
    #    for player in self.players.values():
    #        if entity.issynced:
    #            player.step(game, self, frametime)
    #    for entity in self.entities.values():
    #        if entity.issynced:
    #            entity.step(game, self, frametime)
    #    for entity in self.entities.values():
    #        if entity.issynced:
    #            entity.endstep(game, self, frametime)


    def interpolate(self, prev_state, next_state, alpha):
        if not(0 <= alpha <= 1):
            print("Error: alpha={} while interpolating two states".format(alpha))
            alpha = min(1, max(alpha, 0))
        
        self.next_entity_id = next_state.next_entity_id
        self.time = prev_state.time + (next_state.time - prev_state.time) * alpha

        if alpha < 0.5:
            # Give previous state priority for binary choice (like entity existence)
            self.entities = {id:entity.copy() for id, entity in prev_state.entities.items()}
            self.players = {id:player.copy() for id, player in prev_state.players.items()}
            self.map = prev_state.map
        else:
            # Copy from next_state
            self.entities = {id:entity.copy() for id, entity in next_state.entities.items()}
            self.players = {id:player.copy() for id, player in next_state.players.items()}
            self.map = next_state.map

        for id, entity in self.entities.items():
            if id in prev_state.entities and id in next_state.entities:
                self.entities[id].interpolate(prev_state.entities[id], next_state.entities[id], alpha)

        for id, player in self.players.items():
            if id in prev_state.players and id in next_state.players:
                self.players[id].interpolate(prev_state.players[id], next_state.players[id], alpha)

    def copy(self):
        new = Gamestate()

        new.entities = {id:entity.copy() for id, entity in self.entities.items()}
        new.players = {id:player.copy() for id, player in self.players.items()}
        new.next_entity_id = self.next_entity_id
        new.time = self.time
        new.map = self.map

        return new
