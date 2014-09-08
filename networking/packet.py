#!/usr/bin/env python

from __future__ import division, print_function

# add our main folder as include dir
import sys
sys.path.append("../")

import event_serialize
import constants
import databuffer

class Packet(object):
    def __init__(self, sender):
        self.sequence = None
        self.acksequence = None
        self.time = 0
        self.events = []
        self.sender = sender

    def pack(self):
        packetbuffer = databuffer.Buffer()
        packetbuffer.write("HHf", (self.sequence, self.acksequence, self.time))

        for seq, event in self.events:
            packetbuffer.write("H", seq)
            packetbuffer.write("B", event.eventid)
            packetbuffer.write("f", event.time)
            event.pack(packetbuffer)
        
        return packetbuffer

    def unpack(self, data):
        packetbuffer = databuffer.Buffer()
        packetbuffer.data = data
        
        self.events = []
        statedata = []

        self.sequence, self.acksequence, self.time = packetbuffer.read("HHf")

        while not packetbuffer.is_empty():
            sequence, eventid, time = packetbuffer.read("HBf")

            if self.sender == "client":
                packet_event = object.__new__(event_serialize.clientevents[eventid])
            else:
                packet_event = object.__new__(event_serialize.serverevents[eventid])

            packet_event.unpack(packetbuffer)
            packet_event.time = time

            # Separate states and events
            if eventid in (constants.INPUTSTATE, constants.SNAPSHOT_UPDATE):
                statedata.append((sequence, packet_event))
            else:
                self.events.append((sequence, packet_event))

        # Append the state updates to the end of the normal event list.
        self.events += statedata
