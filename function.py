#!/usr/bin/env python

from __future__ import division, print_function

import math
import mask
import engine.character
import constants

# make pygrafix an optional import
# if we are running the server without sfml everything will work fine
# as long as we don't call functions in the file that use sfml
try:
    import sfml
except: pass

import os.path
import sys

def sign(x):
    # Returns the sign of the number given
    return cmp(x, 0)

def point_direction(x1, y1, x2, y2):
    angle = -math.degrees(math.atan2(y2 - y1, x2 - x1))
    if angle < 0: angle += 360
    return angle

def get_cartesian(angle, length):
    angle *= 180/math.pi
    return (math.cos(angle)*length, math.sin(angle)*length)

def get_polar(x, y):
    return (math.atan2(y/x)*math.pi/180, math.hypot(x, y))

# from http://www.nanobit.net/doxy/quake3/q__math_8c-source.html LerpAngle
def interpolate_angle(a, b, alpha):
    a, b = a % 360, b % 360

    if b - a > 180: b -= 360
    if b - a < -180: b += 360

    return (a + alpha * (b - a)) % 360

masks = {}
def load_mask(filename, give_orig=False):
    if filename in masks:
        if give_orig: return masks[filename]
        else: return masks[filename].copy()

    bitmask = mask.from_image(filename)

    masks[filename] = bitmask

    if give_orig: return bitmask
    else: return bitmask.copy()


textures = {}
def load_texture(filename):
    if filename in textures:
        return textures[filename]

    # Attempt to load the texture from files
    texture = sfml.Texture.from_file(filename)
    textures[filename] = texture

    return texture


def convert_class(class_object):
        # Try converting the class to it's constant first
        if class_object == engine.character.Scout:
            return constants.CLASS_SCOUT
        elif class_object == engine.character.Pyro:
            return constants.CLASS_PYRO
        elif class_object == engine.character.Soldier:
            return constants.CLASS_SOLDIER
        elif class_object == engine.character.Heavy:
            return constants.CLASS_HEAVY
        elif class_object == engine.character.Demoman:
            return constants.CLASS_DEMOMAN
        elif class_object == engine.character.Medic:
            return constants.CLASS_MEDIC
        elif class_object == engine.character.Engineer:
            return constants.CLASS_ENGINEER
        elif class_object == engine.character.Spy:
            return constants.CLASS_SPY
        elif class_object == engine.character.Quote:
            return constants.CLASS_QUOTE

        # Didn't work, try converting the constant to it's class
        if class_object == constants.CLASS_SCOUT:
            return engine.character.Scout
        elif class_object == constants.CLASS_PYRO:
            return engine.character.Pyro
        elif class_object == constants.CLASS_SOLDIER:
            return engine.character.Soldier
        elif class_object == constants.CLASS_HEAVY:
            return engine.character.Heavy
        elif class_object == constants.CLASS_DEMOMAN:
            return engine.character.Demoman
        elif class_object == constants.CLASS_MEDIC:
            return engine.character.Medic
        elif class_object == constants.CLASS_ENGINEER:
            return engine.character.Engineer
        elif class_object == constants.CLASS_SPY:
            return engine.character.Spy
        elif class_object == constants.CLASS_QUOTE:
            return engine.character.Quote
        else:
            print("ERROR: UNKNOWN CLASS ARGUMENT IN Functions.get_class().", class_object)
            return constants.CLASS_SCOUT
