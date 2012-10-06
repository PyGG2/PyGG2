#!/usr/bin/env python

from __future__ import division, print_function

# add our main folder as include dir
import sys
sys.path.append("../")

import struct
import event_serialize
import constants

class Packet(object):
    def __init__(self, sender):
        self.sequence = None
        self.acksequence = None
        self.time = 0
        self.events = []
        self.sender = sender

    def pack(self):
        packetstr = ""

        packetstr += struct.pack(">HHf", self.sequence, self.acksequence, self.time)

        for seq, event in self.events:
            packetstr += struct.pack(">H", seq)
            packetstr += struct.pack(">B", event.eventid)
            packetstr += event.pack()

        return packetstr

    def unpack(self, packetstr):
        self.events = []
        statedata = []

        self.sequence, self.acksequence, self.time = struct.unpack_from(">HHf", packetstr)
        packetstr = packetstr[struct.calcsize(">HHf"):]

        while packetstr:
            sequence, eventid = struct.unpack_from(">HB", packetstr)
            packetstr = packetstr[struct.calcsize(">HB"):]

            if self.sender == "client":
                packet_event = object.__new__(event_serialize.clientevents[eventid])
            else:
                packet_event = object.__new__(event_serialize.serverevents[eventid])

            eventsize = packet_event.unpack(packetstr)
            packetstr = packetstr[eventsize:]

            # Separate states and events
            if eventid in (constants.INPUTSTATE, constants.SNAPSHOT_UPDATE):
                statedata.append((sequence, packet_event))
            else:
                self.events.append((sequence, packet_event))

        # Append the state updates to the end of the normal event list.
        self.events += statedata
