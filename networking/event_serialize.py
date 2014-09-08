from __future__ import division, print_function

import constants
import databuffer

clientevents = {}
serverevents = {}

# decorators to register classes as events, and add time everywhere
def clientevent(cls):
    clientevents[cls.eventid] = cls
    cls.time = 0
    return cls

def serverevent(cls):
    serverevents[cls.eventid] = cls
    cls.time = 0
    return cls

@serverevent
class ServerEventPlayerJoin(object):
    eventid = constants.EVENT_PLAYER_JOIN

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def pack(self, packetbuffer):
        packetbuffer.write("H32p", (self.id, self.name))

    def unpack(self, packetbuffer):
        self.id, self.name = packetbuffer.read("H32p")

@clientevent
class ClientEventHello(object):
    eventid = constants.EVENT_HELLO

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def pack(self, packetbuffer):
        packetbuffer.write("32p32p", (self.name, self.password))

    def unpack(self, packetbuffer):
        self.name, self.password = packetbuffer.read("32p32p")

@serverevent
class ServerEventHello(object):
    eventid = constants.EVENT_HELLO

    def __init__(self, servername, playerid, maxplayers, mapname, version):
        self.servername = servername
        self.playerid = playerid
        self.maxplayers = maxplayers
        self.mapname = mapname
        self.version = version

    def pack(self, packetbuffer):
        packetbuffer.write("32pBB64pH", (self.servername, self.playerid, self.maxplayers, self.mapname, self.version))

    def unpack(self, packetbuffer):
        self.servername, self.playerid, self.maxplayers, self.mapname, self.version = packetbuffer.read("32pBB64pH")

@clientevent
class ClientEventJump(object):
    eventid = constants.EVENT_JUMP

    def pack(self, packetbuffer):
        pass

    def unpack(self, packetbuffer):
        pass

@serverevent
class ServerEventChangeclass(object):
    eventid = constants.EVENT_PLAYER_CHANGECLASS

    def __init__(self, playerid, newclass):
        self.playerid = playerid
        self.newclass = newclass

    def pack(self, packetbuffer):
        packetbuffer.write("HB", (self.playerid, self.newclass))

        return packetbuffer

    def unpack(self, packetbuffer):
        self.playerid, self.newclass = packetbuffer.read("HB")

@clientevent
class ClientEventChangeclass(object):
    eventid = constants.EVENT_PLAYER_CHANGECLASS

    def __init__(self, newclass):
        self.newclass = newclass

    def pack(self, packetbuffer):
        packetbuffer.write("B", self.newclass)

    def unpack(self, packetbuffer):
        self.newclass = packetbuffer.read("B")

@serverevent
class ServerEventSpawn(object):
    eventid = constants.EVENT_PLAYER_SPAWN

    def __init__(self, playerid, x, y):
        self.playerid = playerid
        self.x = x
        self.y = y

    def pack(self, packetbuffer):
        packetbuffer.write("BII", (self.playerid, self.x, self.y))

    def unpack(self, packetbuffer):
        self.playerid, self.x, self.y = packetbuffer.read("BII")

@serverevent
class ServerEventDie(object):
    eventid = constants.EVENT_PLAYER_DIE

    def __init__(self, playerid):
        self.playerid = playerid

    def pack(self, packetbuffer):
        packetbuffer.write("B", self.playerid)

    def unpack(self, packetbuffer):
        self.playerid = packetbuffer.read("B")

@clientevent
class ClientEventInputstate(object):
    eventid = constants.INPUTSTATE

    def __init__(self, internalbuffer):
        self.internalbuffer = internalbuffer

    def pack(self, packetbuffer):
        packetbuffer.write("H", len(self.internalbuffer.data))
        packetbuffer.write("{0}s".format(len(self.internalbuffer.data)), self.internalbuffer.data)

    def unpack(self, packetbuffer):
        length = packetbuffer.read("H")
        self.internalbuffer = databuffer.Buffer(packetbuffer.read("{0}s".format(length)))

@serverevent
class ServerEventSnapshotUpdate(object):
    eventid = constants.SNAPSHOT_UPDATE

    def __init__(self, internalbuffer):
        self.internalbuffer = internalbuffer

    def pack(self, packetbuffer):
        packetbuffer.write("H", len(self.internalbuffer.data))
        packetbuffer.write("{0}s".format(len(self.internalbuffer.data)), self.internalbuffer.data)

    def unpack(self, packetbuffer):
        length = packetbuffer.read("H")
        self.internalbuffer = databuffer.Buffer(packetbuffer.read("{0}s".format(length)))

@serverevent
class ServerEventFullUpdate(object):
    eventid = constants.FULL_UPDATE

    def __init__(self, internalbuffer):
        self.internalbuffer = internalbuffer

    def pack(self, packetbuffer):
        packetbuffer.write("H", len(self.internalbuffer.data))
        packetbuffer.write("{0}s".format(len(self.internalbuffer.data)), self.internalbuffer.data)

    def unpack(self, packetbuffer):
        length = packetbuffer.read("H")
        self.internalbuffer = databuffer.Buffer(packetbuffer.read("{0}s".format(length)))

@clientevent
class ClientEventDisconnect(object):
    eventid = constants.EVENT_PLAYER_DISCONNECT

    def pack(self, packetbuffer):
        pass

    def unpack(self, packetbuffer):
        pass

@serverevent
class ServerEventDisconnect(object):
    eventid = constants.EVENT_PLAYER_DISCONNECT

    def __init__(self, playerid):
        self.playerid = playerid

    def pack(self, packetbuffer):
        packetbuffer.write("B", self.playerid)

    def unpack(self, packetbuffer):
        self.playerid = packetbuffer.read("B")

@serverevent
class ServerEventFirePrimary(object):
    eventid = constants.EVENT_FIRE_PRIMARY

    def __init__(self, playerid):
        self.playerid = playerid

    def pack(self, packetbuffer):
        packetbuffer.write("B", self.playerid)

    def unpack(self, packetbuffer):
        self.playerid = packetbuffer.read("B")

@serverevent
class ServerEventFireSecondary(object):
    eventid = constants.EVENT_FIRE_SECONDARY

    def __init__(self, playerid):
        self.playerid = playerid

    def pack(self, packetbuffer):
        packetbuffer.write("B", self.playerid)

    def unpack(self, packetbuffer):
        self.playerid = packetbuffer.read("B")

@serverevent
class ServerChangeMap(object):
    eventid = constants.EVENT_CHANGE_MAP

    def __init__(self, mapname):
        self.mapname = mapname

    def pack(self, packetbuffer):
        s = bytes(self.mapname)
        packetbuffer.write("B{0}s".format(len(s)), (len(s), s))

    def unpack(self, packetbuffer):
        length = packetbuffer.read("B")
        self.mapname = str(packetbuffer.read("{0}s".format(length)))
