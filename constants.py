from __future__ import division, print_function

# this file contains all kinds of constants

GAME_WIDTH = 800
GAME_HEIGHT = 600

PHYSICS_TIMESTEP = 1/60 # always update physics in these steps

GAME_VERSION_NUMBER = 25000
GAME_VERSION_STRING = "2.7b"
GAME_URL = "http://www.ganggarrison.com/forums/index.php?topic=29530.0"

# Sprites
SPRITE_FOLDER = "sprites/"

# Server
SERVER_MAX_FPS = 1/100

# Rendering
#VSYNC_ENABLED = True
VSYNC_ENABLED = False

# Networking
INPUT_SEND_FPS = 1/30 # we send input to the server at this rate
MAX_PACKET_SIZE = 2048
NETWORK_UPDATE_RATE = 1/40 # the server sends state info to the client at this rate
CLIENT_TIMEOUT = 300
CONNECTION_TIMEOUT = 10
INTERP_BUFFER_LENGTH =  1/10 # The additional lag the client trades for visual smoothness
INTERP_SLIDING_WINDOW = 1/4 # The fraction at which rendering will speed/slow down to meet jitter
MAX_TIME_DESYNC = NETWORK_UPDATE_RATE*2 # The maximum amount of time the client is allowed to lag behind server packets before getting corrected

# Lobby
LOBBY_HOST = "ganggarrison.com"
LOBBY_PORT = 29944

# UUIDs
LOBBY_MESSAGE_TYPE_REG = "b5dae2e8-424f-9ed0-0fcb-8c21c7ca1352"
LOBBY_MESSAGE_TYPE_UNREG = "488984ac-45dc-86e1-9901-98dd1c01c064"
LOBBY_MESSAGE_TYPE_LIST = "297d0df4-430c-bf61-640a-640897eaef57"
GG2_LOBBY_UUID = "0e29560e-443a-93a3-e15e-7bd072df7506" # FIXME: Replace with real one once Medo fixes the lobby
#GG2_LOBBY_UUID = "1ccf16b1-436d-856f-504d-cc1af306aaa7" # Real GG2 UUID
PYGG2_COMPATIBILITY_PROTOCOL = "e8b036bf-409d-a71b-2702-c7e443b1fdbe"

# Networked Events
EVENT_HELLO = 0
EVENT_PLAYER_JOIN = 1
EVENT_PLAYER_LEAVE = 2
FULL_UPDATE = 3
SNAPSHOT_UPDATE = 4
INPUTSTATE = 5
EVENT_PLAYER_CHANGETEAM = 8
EVENT_PLAYER_CHANGECLASS = 9
EVENT_JUMP = 10
EVENT_PLAYER_SPAWN = 11
EVENT_PLAYER_DIE = 12
EVENT_PLAYER_DISCONNECT = 13
EVENT_FIRE_PRIMARY = 14
EVENT_FIRE_SECONDARY = 15
EVENT_CHANGE_MAP = 16

# Class Constants - To use only in networking
CLASS_SCOUT = 0
CLASS_PYRO = 1
CLASS_SOLDIER = 2
CLASS_HEAVY = 3
CLASS_DEMOMAN = 4
CLASS_MEDIC = 5
CLASS_ENGINEER = 6
CLASS_SPY = 7
CLASS_SNIPER = 8
CLASS_QUOTE = 9

# Team Constants
TEAM_SPECTATOR = 0
TEAM_RED = 1
TEAM_BLUE = 2
