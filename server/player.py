from __future__ import division, print_function

# add our main folder as include dir
import sys
sys.path.append("../")

import networking
import engine.player
import constants

class Player(object):
    def __init__(self, networker, game, name, address):
        # generate id
        potentialids = set(range(len(networker.players) + 1))
        takenids = {player.id for player in networker.players.values()}
        self.id = (potentialids - takenids).pop()

        # communication data
        self.address = address
        self.events = []
        self.sequence = 1
        self.server_acksequence = 0
        self.client_acksequence = 0
        self.time_since_update = 0.0

        # register in networker
        networker.players[address] = self

        # and at last add to engine
        player = engine.player.Player(game, game.current_state, self.id)
        player.name = name

    def update(self, networker, game, frametime):
        # Clear the acked stuff from the history
        index = 0
        while index < len(self.events):
            seq, event = self.events[index]
            if seq > self.client_acksequence:
                # This (and all the following events) weren't acked yet. We're done.
                break
            else:
                self.events.pop(index)
                index -= 1
            index += 1

        self.time_since_update += frametime

        if self.time_since_update > constants.NETWORK_UPDATE_RATE:
            self.time_since_update %= constants.NETWORK_UPDATE_RATE
            self.send_packet(networker, game)


    def send_packet(self, networker, game):
        packet = networking.packet.Packet("server")
        packet.sequence = self.sequence
        packet.acksequence = self.server_acksequence
        packet.time = game.current_state.time

        for seq, event in self.events:
            packet.events.append((seq, event))

        # Put state data before event data, for better compression
        snapshot = networker.generate_snapshot_update(game.current_state)
        packet.events.insert(0, (self.sequence, snapshot))

        packetbuffer = packet.pack()# TODO: Compression would be here
        networker.socket.sendto(packetbuffer.data, self.address)

        self.sequence = (self.sequence + 1) % 65535
    
    
    def send_fullupdate(self, networker, game, events):
        packet = networking.packet.Packet("server")
        packet.sequence = self.sequence
        packet.acksequence = self.server_acksequence
        packet.time = game.current_state.time

        for event in events:
            packet.events.append((0, event))
        snapshot = networker.generate_snapshot_update(game.current_state)
        packet.events.append((0, snapshot))
    
        packetbuffer = packet.pack()# TODO: Compression would be here
        networker.socket.sendto(packetbuffer.data, self.address)

        self.sequence = (self.sequence + 1) % 65535


    def destroy(self, networker, game, state):
        player = state.players[self.id]
        player.destroy(game, state)
        event = networking.event_serialize.ServerEventDisconnect(self.id)
        networker.sendbuffer.append(event)
        self.events = []

        del networker.players[self.address]
