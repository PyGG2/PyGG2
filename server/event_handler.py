from __future__ import division, print_function

# add our main folder as include dir
import sys
sys.path.append("../")

import function, constants
from networking import event_serialize

def Client_Event_Changeclass(networker, game, state, senderplayer, event):
    player = state.players[senderplayer.id]
    # TODO: If any, add classlimits here
    newclass = function.convert_class(event.newclass)
    if player.nextclass == newclass:
        return
    player.nextclass = newclass

    classchange_event = event_serialize.ServerEventChangeclass(senderplayer.id, event.newclass)
    game.sendbuffer.append(classchange_event)

    # Kill the character
    try:
        character = state.entities[player.character_id]
        character.die(game, state)
        death_event = event_serialize.ServerEventDie(player.id)
        game.sendbuffer.append(death_event)
    except KeyError:
        # Character is already dead, we don't need to do anything here
        pass

    # Resurrect him with new class. FIXME: REMOVE THIS
    player.spawn(game, state)
    spawn_event = event_serialize.ServerEventSpawn(player.id, 2300, 50)
    game.sendbuffer.append(spawn_event)

def Client_Event_Jump(networker, game, state, senderplayer, event):
    player = state.players[senderplayer.id]
    # TODO: Add lag compensation, if any, here.
    player.up = True

def Client_Inputstate(networker, game, state, senderplayer, event):
    player = state.players[senderplayer.id]
    player.deserialize_input(event.internalbuffer)

def Client_Event_Disconnect(networker, game, state, senderplayer, event):
    player = state.players[senderplayer.id]
    print(player.name +" has disconnected")
    senderplayer.destroy(networker, game, state)

# Gather the functions together to easily be called by the event ID
eventhandlers = {}
eventhandlers[constants.EVENT_PLAYER_CHANGECLASS] = Client_Event_Changeclass
eventhandlers[constants.EVENT_JUMP] = Client_Event_Jump
eventhandlers[constants.INPUTSTATE] = Client_Inputstate
eventhandlers[constants.EVENT_PLAYER_DISCONNECT] = Client_Event_Disconnect
