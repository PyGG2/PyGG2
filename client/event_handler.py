from __future__ import division, print_function

# add our main folder as include dir
import sys
sys.path.append("../")

import struct
import engine.map
import engine.player
import function, constants
from networking import event_serialize


def Server_Event_Hello(client, networker, game, event):
    # Stop saying hello
    networker.has_connected = True
    # TODO: Some version check using event.version and constants.GAME_VERSION_NUMBER
    # Set all the important values to the game
    game.servername = event.servername
    player_id = event.playerid
    game.maxplayers = event.maxplayers
    game.map = engine.map.Map(game, event.mapname)
    client.start_game(player_id)

def Server_Event_Player_Join(client, networker, game, event):
    newplayer = engine.player.Player(game, game.current_state, event.id)
    newplayer.name = event.name

def Server_Event_Changeclass(client, networker, game, event):
    player = game.current_state.players[event.playerid]
    player.nextclass = function.convert_class(event.newclass)

def Server_Event_Die(client, networker, game, event):
    player = game.current_state.players[event.playerid]
    character = game.current_state.entities[player.character_id]
    character.die(game, game.current_state)

def Server_Event_Spawn(client, networker, game, event):
    player = game.current_state.players[event.playerid]
    player.spawn(game, game.current_state)

def Server_Snapshot_Update(client, networker, game, event):
    # Copy the current game state, and replace it with everything the server knows
    packet_time = round(struct.unpack_from(">f", event.bytestr)[0], 5)
    event.bytestr= event.bytestr[4:]

    # Delete all the deprecated old states, they are useless. Remember that list is chronologically ordered
    while len(game.old_states) > 0:
        if game.old_states[0].time < packet_time - constants.PHYSICS_TIMESTEP:
            game.old_states.pop(0)
        else:
            break
    # Also delete those too far ahead, but keep one slightly ahead to be able to interpolate well
    server_current_time = packet_time + networker.estimated_ping
    while len(game.old_states) > 0:
        if game.old_states[-1].time >= packet_time + min(networker.estimated_ping, constants.MAX_EXTRAPOLATION) + constants.PHYSICS_TIMESTEP:
            game.old_states.pop(-1)
        else:
            break

    print("game.old_states:{}".format([s.time for s in game.old_states]))

    if len(game.old_states) > 1:
        old_state_times = [old_state.time for old_state in game.old_states]

        if packet_time in old_state_times:
            # The packet time miraculously is equal one of the stored states
            state = game.old_states[old_state_times.index(packet_time)].copy()
        else:
            # it isn't, we gotta interpolate between the two nearest
            sorted_times = old_state_times
            sorted_times.sort(key=lambda state_time: abs(state_time - packet_time))

            state_1 = game.old_states[old_state_times.index(sorted_times[0])]
            state_2 = game.old_states[old_state_times.index(sorted_times[1])]
            state = state_1.copy()
            state.interpolate(state_1, state_2, (packet_time - sorted_times[0]) / (sorted_times[1] - sorted_times[0]))

    else:
        if len(game.old_states) == 1:
            state = game.old_states[0].copy()
        else:
            # game.old_states is empty
            state = game.current_state.copy()

        # Interpolate to the packet time
        state.update_all_objects(game, packet_time-state.time)

    if state.time != packet_time:
        # Shouldn't happen
        print("\n\nSTATE.TIME != PACKET_TIME; state.time={0}; packet_time={1}; delta={2}\n\n".format(state.time, packet_time, state.time-packet_time))

    #try:
    #    print("{0} < {1} < {2}\n".format(state_1.time, state.time, state_2.time), "packet time:{}\n".format(packet_time), "server time:{}\n".format(packet_time+networker.estimated_ping))
    #except:
    #    print("state.time:{0}\n".format(state.time),"current_state.time:{}\n".format(game.current_state.time), "state.time-current_state.time:{}\n".format(state.time - game.current_state.time), "packet time:{}\n".format(packet_time), "server time:{}\n".format(packet_time+networker.estimated_ping))

    # State should now be exactly what the client thinks should happen at packet_time. Now let the server correct that assumption

    for player in state.players.values():
        length = player.deserialize_input(event.bytestr)
        event.bytestr = event.bytestr[length:]

        try:
            character = state.entities[player.character_id]
            length = character.deserialize(state, event.bytestr)
            event.bytestr = event.bytestr[length:]
        except KeyError:
            # Character is dead; continue
            pass

    # Now we have exactly what happened on the server at packet_time, update it to packet_time+ping (which also happens to be the length of all old_states)

    # BREAKS game.old_states!
    state.update_all_objects(game, networker.estimated_ping)

    # Get rid of the last entry in game.old_states if that is ahead of current state
    try:
        while game.old_states[-1].time >= state.time:
            game.old_states.pop(-1)
    except IndexError:
        pass

    print("END OF THE HANDLER")
    print(state.time, [s.time for s in game.old_states])

    game.current_state = state
    if game.current_state.time != packet_time + networker.estimated_ping:
        print("\n\n\n\ngame.current_state.time={0}; packet_time+networker.estimated_ping={1}; delta={2}".format(game.current_state.time, packet_time + networker.estimated_ping, 20*(game.current_state.time-(packet_time + networker.estimated_ping))))


def Server_Full_Update(client, networker, game, event):
    game.current_state.time, numof_players = struct.unpack_from(">IB", event.bytestr)
    event.bytestr = event.bytestr[5:]

    for index in range(numof_players):
        player = engine.player.Player(game, game.current_state, index)

        player.name, player_class, character_exists = struct.unpack_from(">32pBB", event.bytestr)
        player.nextclass = function.convert_class(player_class)
        event.bytestr = event.bytestr[34:]

        if character_exists:
            player.spawn(game, game.current_state)

def Server_Event_Disconnect(client, networker, game, event):
    player = game.current_state.players[event.playerid]
    print (player.name +" has disconnected")
    player.destroy(game, game.current_state)

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
