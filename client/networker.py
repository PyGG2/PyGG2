from __future__ import division, print_function

# add our main folder as include dir
import sys
sys.path.append("../")

import socket
import constants
import networking.packet
import networking.event_serialize
import event_handler

class Networker(object):
    def __init__(self, server_address, client):
        self.server_address = server_address

        self.events = []
        self.sendbuffer = []
        self.sequence = 1
        self.server_acksequence = 0
        self.client_acksequence = 0

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", 0))
        self.socket.setblocking(False)

        self.has_connected = False
        self.connection_timeout_timer = constants.CLIENT_TIMEOUT

        # Connect to the server, or at least send the hello
        packet = networking.packet.Packet("client")
        packet.sequence = self.sequence
        packet.acksequence = self.client_acksequence
        packet.time = client.game.current_state.time

        event = networking.event_serialize.ClientEventHello(client.player_name, client.server_password)
        packet.events.append((self.sequence, event))
        data = packet.pack()

        numbytes = self.socket.sendto(data, self.server_address)
        if len(data) != numbytes:
            # TODO sane error handling
            print("SERIOUS ERROR, NUMBER OF BYTES SENT != PACKET SIZE AT HELLO")

    def recieve(self, game, client):
        # If we haven't received confirmation that we're connected yet, see if we should try again:
        if not self.has_connected:
            self.connection_timeout_timer -= 1

            if self.connection_timeout_timer <= 0:
                self.connection_timeout_timer = constants.CLIENT_TIMEOUT
                # Send a reminder, in case the first packet was lost
                packet = networking.packet.Packet("client")
                packet.sequence = self.sequence
                packet.acksequence = self.client_acksequence

                event = networking.event_serialize.ClientEventHello(client.player_name, client.server_password)
                packet.events.append((self.sequence, event))
                data = packet.pack()

                numbytes = self.socket.sendto(data, self.server_address)
                if len(data) != numbytes:
                    # TODO sane error handling
                    print("SERIOUS ERROR, NUMBER OF BYTES SENT != PACKET SIZE AT HELLO")


        while True:
            packet = networking.packet.Packet("server")

            try:
                data, sender = self.socket.recvfrom(constants.MAX_PACKET_SIZE)
            except socket.error:
                # recvfrom throws socket.error if there was no packet to read
                break

            # FIXME: Uncomment these as soon as networking debugging is done. I commented this out because it messed with Traceback.
            #try:
            packet.unpack(data)
            #except:
            #    # parse error, don't throw exception but print it
            #    print("Parse error: %s" % sys.exc_info()[1])
            #    continue # drop packet
            
            # Check whether the packet is even new enough
            if packet.sequence <= self.client_acksequence:
                print("Old packet:", packet.time, game.current_state.time)
                # No need to even consider this packet
                return

            # Try to get a template state that's as close to the received one as possible.
            state = None
            if len(game.old_client_states) > 0 and game.current_state.time > packet.time:
                if packet.time < game.old_client_states[0].time:
                    # This packet is extremely old
                    # This shouldn't actually ever happen
                    print("Packet received that is not in game.old_client_states!\nPacket time: {0}\ngame.old_client_states: {1}".format(time, [i.time for i in game.old_client_states]))
                    state = game.old_client_states[0].copy()
                    state.update_all_objects(game, packet.time - state.time)

                # "states" just contains all the states that we can interpolate from
                # That includes the old_client_states and current_state
                states = game.old_client_states[:]
                states.append(game.current_state.copy())

                # Now we sort it as a function of it's closeness to time
                states.sort(key=lambda x: abs(packet.time - x.time))

                # The two first elements of this list will necessarily be those around time
                # So now we cut off everything except the first two
                states = states[:2]
                # And then we sort those normally
                states.sort(key=lambda x: x.time)
                # And then we interpolate
                d_time = (packet.time - states[0].time) * (states[1].time - states[0].time)
                if not(0 <= d_time <= 1):
                    print("This should not happen!\nd_time:{0}\ntime:{1}\nstates[0].time:{2}\nstates[1].time:{3}\n\nold_client_states:{4}\n\n\n".format(d_time, packet.time, states[0].time, states[1].time, [i.time for i in game.old_client_states]))
                states[0].interpolate(states[0], states[1], d_time)
                state = states[0].copy()

            else:
                # We don't even have any old states, just take current_state and try to adapt it
                state = game.current_state.copy()
                state.update_all_objects(game, packet.time - state.time)

            # All old states before this packet are now useless, and all old states after it are wrong
            game.old_client_states = []

            # only accept the packet if the sender is the server
            if sender == self.server_address:
                for seq, event in packet.events:
                    if seq <= self.client_acksequence:
                        # Event has already been processed before, discard
                        continue
                    # process the event
                    event_handler.eventhandlers[event.eventid](client, self, game, state, event)
                game.current_state = state
                game.old_server_states.append(state.copy())
            # otherwise drop the packet
            else:
                print("RECEIVED PACKET NOT FROM ACTUAL SERVER ADDRESS:\nActual Server Address:"+str(self.server_address)+"\nPacket Address:"+str(sender))
                continue

            # ack the packet
            self.client_acksequence = packet.sequence
            self.server_acksequence = packet.acksequence

            # Clear the acked stuff from the history
            index = 0
            while index < len(self.events):
                seq, event = self.events[index]
                if seq > self.server_acksequence:
                    # This (and all the following events) weren't acked yet. We're done.
                    break
                else:
                    del self.events[index]
                    index -= 1
                index += 1


    def generate_inputdata(self, client):
        our_player = client.game.current_state.players[client.our_player_id]
        packetstr = our_player.serialize_input()
        event = networking.event_serialize.ClientEventInputstate(packetstr)
        return event


    def update(self, client):
        # Unload the whole sendbuffer here, and add the sequence
        for event in self.sendbuffer:
            self.events.append((self.sequence, event))
        self.sendbuffer = []

        packet = networking.packet.Packet("client")
        packet.sequence = self.sequence
        packet.acksequence = self.client_acksequence
        packet.time = client.game.current_state.time

        for seq, event in self.events:
            packet.events.append((seq, event))

        if not client.destroy:
            # Prepend the input data if we're not disconnecting
            packet.events.insert(0, (self.sequence, self.generate_inputdata(client)))

        packetstr = ""
        packetstr += packet.pack()

        numbytes = self.socket.sendto(packetstr, self.server_address)
        if len(packetstr) != numbytes:
            # TODO sane error handling
            print("SERIOUS ERROR, NUMBER OF BYTES SENT != PACKET SIZE")

        self.sequence = (self.sequence + 1) % 65535
