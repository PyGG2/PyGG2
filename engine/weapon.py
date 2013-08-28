#!/usr/bin/env python

from __future__ import division, print_function

import math
import struct
import random

import function
import entity
import projectile
import sentry
from networking import event_serialize

# abstract class, don't directly instantiate
class Weapon(entity.Entity):
    def __init__(self, game, state, owner_id):
        super(Weapon, self).__init__(game, state)

        self.owner_id = owner_id
        self.refirealarm = 0.0
        self.reloadalarm = 0.0
        self.ammo = self.maxammo
        self.direction = state.entities[self.owner_id].get_player(state).aimdirection
        self.team = state.entities[self.owner_id].team

        self.issynced = True

    def beginstep(self, game, state, frametime):
        owner = state.entities[self.owner_id]
        self.direction = owner.get_player(state).aimdirection

    def step(self, game, state, frametime):
        owner = state.entities[self.owner_id]

        self.reload(game, state, frametime)

        if game.isserver:
            if owner.get_player(state).leftmouse and self.refirealarm == 0:
                self.fire_primary(game, state)
                event = event_serialize.ServerEventFirePrimary(owner.player_id)
                game.sendbuffer.append(event)

            if owner.get_player(state).rightmouse and self.refirealarm == 0:
                self.fire_secondary(game, state)
                event = event_serialize.ServerEventFireSecondary(owner.player_id)
                game.sendbuffer.append(event)

    def reload(self, game, state, frametime):
        if self.refirealarm <= 0:
            self.refirealarm = 0.0
        else:
            self.refirealarm -= frametime
        
        if self.reloadalarm <= 0:
            self.ammo = min(self.maxammo, self.ammo+1)
            if self.ammo < self.maxammo:
                self.reloadalarm = self.reloadtime
        else:
            self.reloadalarm -= frametime

    # override this
    def fire_primary(self, game, state): pass
    def fire_secondary(self, game, state): pass

    def interpolate(self, prev_obj, next_obj, alpha):
        self.refirealarm = (1 - alpha) * prev_obj.refirealarm + alpha * next_obj.refirealarm
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

    def serialize(self, state):
        packetstr = ""
        packetstr += struct.pack(">Bf", self.ammo, self.reloadalarm)
        return packetstr

    def deserialize(self, state, packetstr):
        self.ammo, self.reloadalarm = struct.unpack_from(">Bf", packetstr)
        packetstr = packetstr[5:]
        return 5

class Scattergun(Weapon):
    maxammo = 6
    refiretime = .5
    reloadtime = 1
    shotdamage = 8

    def fire_primary(self, game, state):
        if self.ammo > 0:
            owner = state.entities[self.owner_id]
            random.seed(str(owner.get_player(state).id) + ";" + str(state.time))

            for i in range(10):
                direction = owner.get_player(state).aimdirection + (7 - random.randint(0, 15))

                # add user speed to bullet speed but don't change direction of the bullet
                playerdir = math.degrees(math.atan2(-owner.vspeed, owner.hspeed))
                diffdir = direction - playerdir
                playerspeed = math.hypot(owner.hspeed, owner.vspeed)
                speed = 330 + random.randint(0, 4)*30 + math.cos(math.radians(diffdir)) * playerspeed

                projectile.Shot(game, state, self.id, self.shotdamage, direction, speed)

            self.refirealarm = self.refiretime
            self.reloadalarm = self.reloadtime
            self.ammo = max(0, self.ammo-1)

class Flamethrower(Weapon):
    maxammo = 200
    refiretime = 1/30
    reloadtime = 3/4
    length = 40 # Flamethrower sprite length

    def fire_primary(self, game, state):
        projectile.Flame(game, state, self.id)
        self.refirealarm = self.refiretime

class Rocketlauncher(Weapon):
    maxammo = 4
    refiretime = 1
    reloadtime = 5/6

    def fire_primary(self, game, state):
        if self.ammo > 0:
            projectile.Rocket(game, state, self.id)
            self.refirealarm = self.refiretime
            self.reloadalarm = self.reloadtime
            self.ammo = max(0, self.ammo-1)

class Minigun(Weapon):
    maxammo = 200
    refiretime = 1/15
    reloadtime = 1/2
    shotdamage = 8

    def fire_primary(self, game, state):
        if self.ammo > 0:
            owner = state.entities[self.owner_id]
            random.seed(str(owner.get_player(state).id) + ";" + str(state.time))

            direction = owner.get_player(state).aimdirection + (7 - random.randint(0, 14))
            speed = 360 + random.randint(0, 1)*30

            projectile.Shot(game, state, self.id, self.shotdamage, direction, speed)

            self.refirealarm = self.refiretime

class Shotgun(Weapon):
    maxammo = 4
    refiretime = 2/3
    reloadtime = 1/2
    shotdamage = 7

    def fire_primary(self, game, state):
        if self.ammo > 0:
            owner = state.entities[self.owner_id]
            random.seed(str(owner.get_player(state).id) + ";" + str(state.time))
            for i in range(5):
                direction = owner.get_player(state).aimdirection + (5 - random.randint(0, 11))

                # add user speed to bullet speed but don't change direction of the bullet
                playerdir = math.degrees(math.atan2(-owner.vspeed, owner.hspeed))
                diffdir = direction - playerdir
                playerspeed = math.hypot(owner.hspeed, owner.vspeed)
                speed = 330 + random.randint(0, 4)*30 + math.cos(math.radians(diffdir)) * playerspeed

                projectile.Shot(game, state, self.id, self.shotdamage, direction, speed)

            self.refirealarm = self.refiretime
            self.reloadalarm = self.reloadtime
            self.ammo = max(0, self.ammo-1)

    def fire_secondary(self, game, state):
        owner = state.entities[self.owner_id]
        if owner.sentry != None:
            owner.sentry.destroy(state)
        owner.sentry = sentry.Building_Sentry(game, state, owner)

class Medigun(Weapon):
    maxammo = 40
    refiretime = 0.05
    reloadtime = 1
    shotdamage = 4

    def fire_secondary(self, game, state):
        if self.ammo > 0:
            owner = state.entities[self.owner_id]
            random.seed(str(owner.get_player(state).id) + ";" + str(state.time))

            direction = owner.get_player(state).aimdirection + (5 - random.randint(0, 11))

            # add user speed to needle speed but don't change direction of the bullet
            playerdir = math.degrees(math.atan2(-owner.vspeed, owner.hspeed))
            diffdir = direction - playerdir
            playerspeed = math.hypot(owner.hspeed, owner.vspeed)
            speed = 330 + random.randint(0, 4)*30 + math.cos(math.radians(diffdir)) * playerspeed

            projectile.Needle(game, state, self.id, self.shotdamage, direction, speed)

            self.refirealarm = self.refiretime
            self.reloadalarm = self.reloadtime
            self.ammo = max(0, self.ammo-1)
    
    def reload(self, game, state, frametime):
        if self.refirealarm <= 0:
            self.refirealarm = 0.0
        else:
            self.refirealarm -= frametime
        
        if self.reloadalarm <= 0:
            self.ammo = self.maxammo
        else:
            self.reloadalarm -= frametime

class Revolver(Weapon):
    maxammo = 6
    refiretime = 3/5
    reloadtime = .5

    def fire_primary(self, game, state):
        if self.ammo > 0:
            owner = state.entities[self.owner_id]
            if not owner.cloaking:
                random.seed(str(owner.player_id) + ";" + str(state.time))
                direction = owner.get_player(state).aimdirection + (1 - random.randint(0, 2))
                projectile.Shot(game, state, self.id, damage=28, direction=direction, speed=630)
                self.refirealarm = self.refiretime
                self.reloadalarm = self.reloadtime
                self.ammo = max(0, self.ammo-1)
            #else: Stab

    def fire_secondary(self, game, state):
        owner = state.entities[self.owner_id]
        owner.cloaking = not owner.cloaking# Any ideas how to add a good gradient?
        print("Cloaking: ", owner.cloaking, "| is very unresponsive because it doesn't check for pressing, just whether RMB is being held.")

class Blade(Weapon):
    maxammo = 4
    refiretime = 1
    reloadtime = 5/6

    def fire_primary(self, game, state):
        projectile.Blade(game, state, self.id)
        self.refirealarm = self.refiretime
