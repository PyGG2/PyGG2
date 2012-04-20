#!/usr/bin/env python

from __future__ import division, print_function

import entity
import mask
import character
import math
import function

class Building_Sentry(entity.MovingObject):
    max_hp = 100 # Maximum hitpoints the sentry can ever have
    starting_hp = 25 # At what hitpoints the sentry will start building
    collision_mask = mask.Mask(26, 19, True) # TODO: Implement changing masks
    build_time = 2 # Number of secs it takes to build
    hp_increment = (max_hp-starting_hp)/build_time
    animation_increment = 10/build_time # 10 == number of frames in sentry build animation

    def __init__(self, game, state, owner):
        super(Building_Sentry, self).__init__(game, state)

        self.hp = self.starting_hp
        self.isfalling = True
        self.animation_frame = 0
        self.building_time = 0

        self.owner_id = owner.id
        character = state.entities[owner.character_id]
        self.x = character.x
        self.y = character.y
        
        if character.flip == True:
            self.flip = True
        else:
            self.flip = False

    def step(self, game, state, frametime):
        if self.isfalling:
            # If we've hit the floor, get us back out and build
            while game.map.collision_mask.overlap(self.collision_mask, (int(self.x), int(self.y))):
                self.y -= 1
                self.isfalling = False

            # Gravity
            self.vspeed += 300 * frametime

            # TODO: air resistance, not hard limit
            self.vspeed = min(800, self.vspeed)

        if not self.isfalling:
            self.hspeed = 0
            self.vspeed = 0

            if self.hp <= 0:
                self.destroy(state)
                return

            if self.building_time >= self.build_time:
                # Cap hp at max hp
                if self.hp >= self.max_hp:
                    self.hp = self.max_hp
                # Create a finished sentry, and destroy the building sentry object
                owner = state.players[self.owner_id]
                owner.sentry = Sentry(game, state, self.owner_id, self.x, self.y, self.hp, self.flip)
                self.destroy(state)
            else:
                # Continue building
                self.hp += self.hp_increment * frametime
                self.building_time += frametime
                self.animation_frame += self.animation_increment * frametime

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Building_Sentry, self).interpolate(prev_obj, next_obj, alpha)
        self.animation_frame = prev_obj.animation_frame + (next_obj.animation_frame - prev_obj.animation_frame) * alpha
        self.hp = prev_obj.hp + (next_obj.hp - prev_obj.hp) * alpha
        self.build_time = prev_obj.build_time + (next_obj.build_time - prev_obj.build_time) * alpha

    def destroy(self, state):
        # TODO: Sentry destruction syncing, bubble
        super(Building_Sentry, self).destroy(state)
        owner = state.players[self.owner_id]
        owner.sentry = None


class Sentry(entity.MovingObject):
    collision_mask = mask.Mask(26, 19, True)

    def __init__(self, game, state, owner_id, x, y, hp, flip):
        super(Sentry, self).__init__(game, state)
        self.owner_id = owner_id
        self.aiming_direction = 0
        self.x = x
        self.y = y
        self.hp = hp
        self.flip = flip
        self.detection_radius = 375
        
        
        self.rotating = False
        self.turret_flip = flip
        
        self.rotatestart = 0
        self.rotateend = 4
        self.rotateindex = self.rotatestart;
        self.default_direction = 180 * self.flip
        self.direction = self.default_direction
        
        #targetting Queue
        self.nearest_target = -1
        self.target_queue = []
        
    def step(self, game, state, frametime):
        
        # TODO: Aim at nearest enemy
        
        if self.hp <= 0:
            self.destroy(state)
        self.target_queue = [] #clear the list
        for obj in state.entities.values():
                if isinstance(obj, character.Character) and math.hypot(self.x-obj.x,self.y - obj.y) <= self.detection_radius:
                    target_tuple = (obj, math.hypot(self.x-obj.x,self.y - obj.y))
                    self.target_queue.append(target_tuple)
        if len(self.target_queue) > 0: #TODO: implement point_direction and adjust priorities accordingly
            self.target_queue.sort(key= lambda distance: distance[1]) #sort by the second item in the tuples; distance
            self.nearest_target = self.target_queue[0][0] #get the first part of tuple
            target_character = state.entities[self.nearest_target.id]
            target_angle = function.point_direction(self.x,self.y,target_character.x,target_character.y)
            self.direction = target_angle
            if target_character.x > self.x and self.turret_flip == True:
                self.rotating = True
            elif target_character.x < self.x and self.turret_flip == False:
                self.rotating = True
        else:
            self.nearest_target = -1
            
        if self.nearest_target == -1 and self.flip != self.turret_flip: #reset to old position
            self.rotating = True
            self.direction = self.default_direction
            
        if self.rotating == True:
            self.rotateindex += 0.15
            if (self.rotateindex >= self.rotateend):
                self.rotating = False
                self.turret_flip = not self.turret_flip
                self.rotateindex = self.rotatestart
    def interpolate(self, prev_obj, next_obj, alpha):
        super(Sentry, self).interpolate(prev_obj, next_obj, alpha)
        self.hp = prev_obj.hp + (next_obj.hp - prev_obj.hp) * alpha
        self.direction = prev_obj.direction + (next_obj.direction - prev_obj.direction) * alpha
        self.rotating = next_obj.rotating
        self.rotateindex = prev_obj.rotateindex + (next_obj.rotateindex - prev_obj.rotateindex) * alpha
        self.turret_flip = next_obj.turret_flip
    def destroy(self, state):
        # TODO: Sentry destruction syncing, bubble
        super(Sentry, self).destroy(state)
        owner = state.players[self.owner_id]
        owner.sentry = None
