#!/usr/bin/env python

from __future__ import division, print_function

import math
import random

import entity
import character
import function
import mask
import constants

class Shot(entity.MovingObject):
    shot_hitmasks = {}

    fade_time = 0.8 # seconds of fading when max_flight_time is being reached
    max_flight_time = 1.5

    def __init__(self, game, state, sourceweapon_id, damage, direction, speed):
        super(Shot, self).__init__(game, state)

        self.direction = 0.0
        self.flight_time = 0.0
        self.sourceweapon_id = sourceweapon_id
        self.damage = damage
        self.team = state.entities[self.sourceweapon_id].team

        srcwep = state.entities[sourceweapon_id]
        srcchar = state.entities[srcwep.owner_id]

        self.x = srcchar.x
        self.y = srcchar.y+8

        self.direction = direction

        self.hspeed = math.cos(math.radians(self.direction)) * speed
        self.vspeed = math.sin(math.radians(self.direction)) * -speed

    def step(self, game, state, frametime):
        # gravitational force
        self.vspeed += 4.5 * frametime

        # calculate direction
        self.direction = function.point_direction(self.x - self.hspeed, self.y - self.vspeed, self.x, self.y)

    def endstep(self, game, state, frametime):
        super(Shot, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(round(self.direction)) % 360
        if angle in self.shot_hitmasks:
            mask = self.shot_hitmasks[angle]
        else:
            mask = function.load_mask(constants.SPRITE_FOLDER + "projectiles/shots/0.png").rotate(angle)
            self.shot_hitmasks[angle] = mask

        # FIXME: "and self.flight_time > constants.PHYSICS_TIMESTEP" is an extremely hacky way to prevent negative time collisions. Is there a better method?
        if ((state.map.collision_mask.overlap(mask, (int(round(self.x)), int(round(self.y))))) and self.flight_time >= constants.PHYSICS_TIMESTEP) or self.flight_time >= self.max_flight_time:
            # calculate unit speeds (speeds normalized into the range 0-1)
            h_unit_speed = math.cos(math.radians(self.direction))
            v_unit_speed = -math.sin(math.radians(self.direction))
        
            x, y = self.x, self.y
        
            # move back until we're not colliding anymore - this is the colliding point
            while state.map.collision_mask.overlap(mask, (int(round(x)), int(round(y)))):
                x -= h_unit_speed
                y -= v_unit_speed
        
            self.destroy(state)

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Shot, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha


class Needle(entity.MovingObject):
    shot_hitmasks = {}

    fade_time = 0.8 # seconds of fading when max_flight_time is being reached
    max_flight_time = 3

    def __init__(self, game, state, sourceweapon_id, damage, direction, speed):
        super(Needle, self).__init__(game, state)

        self.direction = 0.0
        self.flight_time = 0.0
        self.sourceweapon_id = sourceweapon_id
        self.damage = damage
        self.team = state.entities[self.sourceweapon_id].team

        srcwep = state.entities[sourceweapon_id]
        srcchar = state.entities[srcwep.owner_id]

        self.x = srcchar.x
        self.y = srcchar.y+8

        self.direction = direction

        self.hspeed = math.cos(math.radians(self.direction)) * speed
        self.vspeed = math.sin(math.radians(self.direction)) * -speed

    def step(self, game, state, frametime):
        # gravitational force
        self.vspeed += 4.5 * frametime

        # calculate direction
        self.direction = function.point_direction(self.x - self.hspeed, self.y - self.vspeed, self.x, self.y)

    def endstep(self, game, state, frametime):
        super(Needle, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(round(self.direction)) % 360
        if angle in self.shot_hitmasks:
            mask = self.shot_hitmasks[angle]
        else:
            mask = function.load_mask(constants.SPRITE_FOLDER + "projectiles/needles/0.png").rotate(angle)
            self.shot_hitmasks[angle] = mask

        # FIXME: "and self.flight_time > constants.PHYSICS_TIMESTEP" is an extremely hacky way to prevent negative time collisions. Is there a better method?
        if ((state.map.collision_mask.overlap(mask, (int(round(self.x)), int(round(self.y))))) and self.flight_time >= constants.PHYSICS_TIMESTEP) or self.flight_time > self.max_flight_time:
            # calculate unit speeds (speeds normalized into the range 0-1)
            h_unit_speed = math.cos(math.radians(self.direction))
            v_unit_speed = -math.sin(math.radians(self.direction))

            x, y = self.x, self.y

            # move back until we're not colliding anymore - this is the colliding point
            while state.map.collision_mask.overlap(mask, (int(x), int(y))):
                x -= h_unit_speed
                y -= v_unit_speed

            self.destroy(state)

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Needle, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha


class Rocket(entity.MovingObject):
    rocket_hitmasks = {}

    fade_time = .3 # seconds of fading when max_flight_time is being reached
    max_flight_time = 20

    damage = 35
    blastradius = 65
    knockback = 240

    def __init__(self, game, state, sourceweapon_id):
        super(Rocket, self).__init__(game, state)

        self.direction = 0.0
        self.flight_time = 0.0
        self.sourceweapon_id = sourceweapon_id
        self.team = state.entities[self.sourceweapon_id].team

        srcwep = state.entities[sourceweapon_id]
        srcchar = state.entities[srcwep.owner_id]

        self.x = srcchar.x
        self.y = srcchar.y

        self.direction = srcwep.direction

        self.speed = 390
        self.hspeed = math.cos(math.radians(self.direction)) * self.speed
        self.vspeed = math.sin(math.radians(self.direction)) * -self.speed

    def destroy(self, game, state, frametime):
        if not self.max_flight_time - self.flight_time < self.fade_time:
            for obj in state.entities.values():
                if isinstance(obj, character.Character) and math.hypot(self.x - obj.x, self.y - obj.y) < self.blastradius:

                    # w and h are the width and height of the collision mask of the character
                    w, h = obj.collision_mask.get_size()

                    # x and y are here a vector from the rocket to the character
                    x = self.x-obj.x
                    y = self.y-obj.y

                    # we try to find out the crosspoint of that vector with the collision rectangle
                    f = w/(2*x)
                    if abs(f*y) < h/2:
                        # the vector crosses the rectangle at the sides
                        x = function.sign(x)*w/2
                        y *= f
                    else:
                        # the vector crosses the rectangle at the bottom or top
                        f = h/(2*y)
                        x *= f
                        y = function.sign(y)*h/2

                    # x and y are now the positions of the point on the edge of the collision rectangle nearest to the rocket

                    # now get the vector from the rocket to that point, and store it in x and y
                    x = (obj.x+x) - self.x
                    y = (obj.y+y) - self.y

                    length = math.hypot(x, y)
                    force = (1 - (length/self.blastradius)) * self.knockback
                    obj.hspeed += force*(x/length)
                    obj.vspeed += force*(y/length)

        super(Rocket, self).destroy(state)

    def step(self, game, state, frametime):
        # FIXME: MAKE THIS WORK FOR NEGATIVE frametime!
        # GMK-GG2 tried to emulate basic acceleration and air resistance with two simple instructions:
        #   [execute 30 times per second]
        #   speed += 1
        #   speed *= 0.92
        # Underneath is the same thing converted to work with frametime.
        # PS: If you ever have the chance, please bash whoever had the idea of a non-standard exponential function for a rocket in an 8-bit game on the head. Thank you.
        self.speed /= 30
        n = 30 * frametime
        self.speed = (0.92**n) * self.speed + 0.92*((1 - (0.92**n))/(1 - 0.92))
        self.speed *= 30

        self.hspeed = math.cos(math.radians(self.direction)) * self.speed * function.sign(frametime)
        self.vspeed = math.sin(math.radians(self.direction)) * (-self.speed) * function.sign(frametime)

    def endstep(self, game, state, frametime):
        super(Rocket, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(round(self.direction)) % 360
        if angle in self.rocket_hitmasks:
            mask = self.rocket_hitmasks[angle]
        else:
            mask = function.load_mask(constants.SPRITE_FOLDER + "projectiles/rockets/0.png").rotate(angle)
            self.rocket_hitmasks[angle] = mask

        # FIXME: "and self.flight_time > constants.PHYSICS_TIMESTEP" is an extremely hacky way to prevent negative time collisions. Is there a better method?
        if ((state.map.collision_mask.overlap(mask, (int(round(self.x)), int(round(self.y))))) and self.flight_time >= constants.PHYSICS_TIMESTEP) or self.flight_time >= self.max_flight_time:
            self.destroy(game, state, frametime)

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Rocket, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha


class Mine(entity.MovingObject):
    mine_hitmasks = {}
    damage = 45
    blastradius = 40
    knockback = 240
    speed = 360
    gravity = 6
    
    def __init__(self, game, state, sourceweapon_id):
        super(Mine, self).__init__(game, state)
        
        self.sourceweapon_id = sourceweapon_id
        self.team = state.entities[self.sourceweapon_id].team
        
        srcwep = state.entities[sourceweapon_id]
        srcchar = state.entities[srcwep.owner_id]
        
        self.x = srcchar.x
        self.y = srcchar.y
        
        self.direction = srcwep.direction
        self.hspeed = math.cos(math.radians(self.direction)) * self.speed
        self.vspeed = math.sin(math.radians(self.direction)) * -self.speed
        
        self.stickied = False
        self.flight_time = 0

    def destroy(self, game, state):
        for obj in state.entities.values():
            if isinstance(obj, character.Character) and math.hypot(self.x - obj.x, self.y - obj.y) < self.blastradius:

                # w and h are the width and height of the collision mask of the character
                w, h = obj.collision_mask.get_size()

                # x and y are here a vector from the rocket to the character
                x = self.x-obj.x
                y = self.y-obj.y

                # we try to find out the crosspoint of that vector with the collision rectangle
                f = w/(2*x)
                if abs(f*y) < h/2:
                    # the vector crosses the rectangle at the sides
                    x = function.sign(x)*w/2
                    y *= f
                else:
                    # the vector crosses the rectangle at the bottom or top
                    f = h/(2*y)
                    x *= f
                    y = function.sign(y)*h/2

                # x and y are now the positions of the point on the edge of the collision rectangle nearest to the rocket

                # now get the vector from the rocket to that point, and store it in x and y
                x = (obj.x+x) - self.x
                y = (obj.y+y) - self.y

                length = math.hypot(x, y)
                force = (1 - (length/self.blastradius)) * self.knockback
                obj.hspeed += force*(x/length)
                obj.vspeed += force*(y/length)

        srcwep = state.entities[self.sourceweapon_id]
        srcwep.mines.pop(srcwep.mines.index(self))
        super(Mine, self).destroy(state)

    def step(self, game, state, frametime):
        if not self.stickied:
            self.vspeed += self.gravity*frametime

    def endstep(self, game, state, frametime):
        super(Mine, self).endstep(game, state, frametime)
        self.flight_time += frametime

        angle = int(round(self.direction)) % 360
        if angle in self.mine_hitmasks:
            mask = self.mine_hitmasks[angle]
        else:
            mask = function.load_mask(constants.SPRITE_FOLDER + "projectiles/rockets/0.png").rotate(angle)
            self.mine_hitmasks[angle] = mask

        # FIXME: "and self.flight_time > constants.PHYSICS_TIMESTEP" is an extremely hacky way to prevent negative time collisions. Is there a better method?
        if ((state.map.collision_mask.overlap(mask, (int(round(self.x)), int(round(self.y))))) and self.flight_time >= constants.PHYSICS_TIMESTEP):
            stickied = True
            self.hspeed = 0
            self.vspeed = 0

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Mine, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha


class Flame(entity.MovingObject):
    flame_hitmasks = {}
    max_flight_time = 1/2
    damage = 3.3

    def __init__(self, game, state, sourceweapon_id):
        super(Flame, self).__init__(game, state)

        self.flight_time = 0.0
        self.sourceweapon_id = sourceweapon_id
        self.team = state.entities[self.sourceweapon_id].team

        srcwep = state.entities[sourceweapon_id]
        srcchar = state.entities[srcwep.owner_id]

        self.x = srcchar.x + srcwep.length * math.cos(srcwep.direction*math.pi/180)
        self.y = srcchar.y - srcwep.length * math.sin(srcwep.direction*math.pi/180)

        self.direction = (srcwep.direction + (10-random.randint(0, 20))) % 360

        self.speed = 150 + random.randint(0, 150)
        self.hspeed = math.cos(math.radians(self.direction)) * self.speed + srcchar.hspeed
        self.vspeed = math.sin(math.radians(self.direction)) * -self.speed + srcchar.vspeed


    def step(self, game, state, frametime):
        #Gravitational force
        self.vspeed += 4.5*frametime

    def endstep(self, game, state, frametime):
        super(Flame, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(round(self.direction))

        if angle in self.flame_hitmasks:
            mask = self.flame_hitmasks[angle]
        else:
            mask = function.load_mask(constants.SPRITE_FOLDER + "projectiles/flames/0.png").rotate(angle)
            self.flame_hitmasks[angle] = mask

        # FIXME: "and self.flight_time > constants.PHYSICS_TIMESTEP" is an extremely hacky way to prevent negative time collisions. Is there a better method?
        if ((state.map.collision_mask.overlap(mask, (int(round(self.x)), int(round(self.y))))) and self.flight_time >= constants.PHYSICS_TIMESTEP) or self.flight_time > self.max_flight_time:
            self.destroy(state)


    def interpolate(self, prev_obj, next_obj, alpha):
        super(Flame, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha

class Blade(entity.MovingObject):
    shot_hitmasks = {}

    max_flight_time = 3
    damage = 35
    blastradius = 65
    knockback = 240

    def __init__(self, game, state, sourceweapon_id):
        super(Blade, self).__init__(game, state)

        self.direction = 0.0
        self.flight_time = 0.0
        self.sourceweapon_id = sourceweapon_id
        self.team = state.entities[self.sourceweapon_id].team

        srcwep = state.entities[sourceweapon_id]
        srcchar = state.entities[srcwep.owner_id]

        self.x = srcchar.x
        self.y = srcchar.y+8

        self.direction = srcwep.direction

        speed = 700
        self.hspeed = math.cos(math.radians(self.direction)) * speed
        self.vspeed = math.sin(math.radians(self.direction)) * -speed

    def step(self, game, state, frametime):

        # calculate direction
        self.direction = function.point_direction(self.x - self.hspeed, self.y - self.vspeed, self.x, self.y)

    def endstep(self, game, state, frametime):
        super(Blade, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(round(self.direction)) % 360
        if angle in self.shot_hitmasks:
            mask = self.shot_hitmasks[angle]
        else:
            mask = function.load_mask(constants.SPRITE_FOLDER + "projectiles/needles/0.png").rotate(angle)
            self.shot_hitmasks[angle] = mask

        # FIXME: "and self.flight_time > constants.PHYSICS_TIMESTEP" is an extremely hacky way to prevent negative time collisions. Is there a better method?
        if ((state.map.collision_mask.overlap(mask, (int(round(self.x)), int(round(self.y))))) and self.flight_time >= constants.PHYSICS_TIMESTEP) or self.flight_time >= self.max_flight_time:
            # calculate unit speeds (speeds normalized into the range 0-1)
            h_unit_speed = math.cos(math.radians(self.direction))
            v_unit_speed = -math.sin(math.radians(self.direction))

            x, y = self.x, self.y

            # move back until we're not colliding anymore - this is the colliding point
            while state.map.collision_mask.overlap(mask, (int(round(x)), int(round(y)))):
                x -= h_unit_speed
                y -= v_unit_speed

            self.destroy(state)

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Blade, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha
