from __future__ import division, print_function

# add our main folder as include dir
import sys
sys.path.append("../")

import struct
import engine.map
import engine.player
import function, constants
from networking import event_serialize


def Server_Event_Hello(client, networker, game, state, event):
    # Stop saying hello
    networker.has_connected = True
    # TODO: Some version check using event.version and constants.GAME_VERSION_NUMBER
    # Set all the important values to the game
    game.servername = event.servername
    player_id = event.playerid
    game.maxplayers = event.maxplayers
    game.map = engine.map.Map(game, event.mapname)
    client.start_game(player_id, state)

def Server_Event_Player_Join(client, networker, game, state, event):
    newplayer = engine.player.Player(game, state, event.id)
    newplayer.name = event.name
    
def Server_Event_Changeclass(client, networker, game, state, event):
    player = state.players[event.playerid]
    player.nextclass = function.convert_class(event.newclass)

def Server_Event_Die(client, networker, game, state, event):
    player = state.players[event.playerid]
    character = state.entities[player.character_id]
    character.die(game, state)

def Server_Event_Spawn(client, networker, game, state, event):
    player = state.players[event.playerid]
    player.spawn(game, state)

def Server_Snapshot_Update(client, networker, game, state, event):
    for player in state.players.values():
        length = player.deserialize_input(event.bytestr)
        event.bytestr = event.bytestr[length:]
        
        try:
            character = state.entities[player.character_id]
            length = character.deserialize(state, event.bytestr)
            event.bytestr = event.bytestr[length:]
        except KeyError:
            # Character is dead
            pass

def Server_Full_Update(client, networker, game, state, event):
    numof_players = struct.unpack_from(">B", event.bytestr)[0]
    event.bytestr = event.bytestr[1:]
    # FIXME: Unclean mixing
    game.rendering_time = event.time

    for index in range(numof_players):
        player = engine.player.Player(game, state, index)
        player.name, player_class, character_exists = struct.unpack_from(">32pBB", event.bytestr)
        player.nextclass = function.convert_class(player_class)
        event.bytestr = event.bytestr[34:]
        
        if character_exists:
            player.spawn(game, state)

def Server_Event_Disconnect(client, networker, game, state, event):
    player = state.players[event.playerid]
    print (player.name +" has disconnected")
    player.destroy(game, state)

def Server_Event_Fire_Primary(client, networker, game, state, event):
    player = state.players[event.playerid]
    try:
        character = state.entities[player.character_id]
        weapon = state.entities[character.weapon_id]
        weapon.fire_primary(game, state)
    except IndexError:
        # character is dead or something. Shouldn't happen, so print something
        print("Error: Firing event called for dead or non-existent character!")

def Server_Event_Fire_Secondary(client, networker, game, state, event):
    player = state.players[event.playerid]
    try:
        character = state.entities[player.character_id]
        weapon = state.entities[character.weapon_id]
        weapon.fire_secondary(game, state)
    except IndexError:
        # character is dead or something. Shouldn't happen, so print something
        print("Error: Firing event called for dead or non-existent character!")

def Server_Event_Change_Map(client, networker, game, state, event):
    state.map = engine.map.Map(game, event.mapname)


# Gather the functions together to easily be called by the event ID
eventhandlers = {}
eventhandlers[constants.EVENT_HELLO] = Server_Event_Hello
eventhandlers[constants.EVENT_PLAYER_JOIN] = Server_Event_Player_Join
eventhandlers[constants.EVENT_PLAYER_CHANGECLASS] = Server_Event_Changeclass
eventhandlers[constants.EVENT_PLAYER_DIE] = Server_Event_Die
eventhandlers[constants.EVENT_PLAYER_SPAWN] = Server_Event_Spawn
eventhandlers[constants.SNAPSHOT_UPDATE] = Server_Snapshot_Update
eventhandlers[constants.FULL_UPDATE] = Server_Full_Update
eventhandlers[constants.EVENT_PLAYER_DISCONNECT] = Server_Event_Disconnect
eventhandlers[constants.EVENT_FIRE_PRIMARY] = Server_Event_Fire_Primary
eventhandlers[constants.EVENT_FIRE_SECONDARY] = Server_Event_Fire_Secondary
eventhandlers[constants.EVENT_CHANGE_MAP] = Server_Event_Change_Map
