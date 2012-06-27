import webbrowser
import socket
import uuid
import struct
import random
import sfml

import constants
import function
from .handler import Handler
from .spritefont import SpriteFont
from .main import GameClientHandler

# generic menu handler
class MenuHandler(Handler):
    menuitems = []
    offsetx = 30
    offsety = 30
    spacing = 30

    def __init__(self, window, manager):
        self.manager = manager
        self.window = window

        self.font = SpriteFont(bold=True)
        self.prevleft = None
        
        self.window_focused = True
        self.joke_counter = 0

        self.window.title = 'PyGG2 - ??? FPS:'

    def draw(self, hoveritem=None):
        x = self.offsetx
        y = self.offsety
        for item in self.menuitems:
            if item is hoveritem:
                width, height = self.font.stringSize(item[0])
                rect = sfml.RectangleShape((width, height))
                rect.fill_color = sfml.Color.RED
                rect.position = (x, y)
                self.window.draw(rect)
            self.font.renderString(item[0], self.window, x, y)
            y += self.spacing

        self.window.display()

    def step(self):

        # check if user exited the game
        if not self.window.open or sfml.Keyboard.is_key_pressed(sfml.Keyboard.ESCAPE):
            return False
        for event in self.window.iter_events():
            if event.type == sfml.Event.CLOSED: #Press the 'x' button
                return False
            elif event.type == sfml.Event.LOST_FOCUS:
                self.window_focused = False
            elif event.type == sfml.Event.GAINED_FOCUS:
                self.window_focused = True
            elif event.type == sfml.Event.KEY_PRESSED: #Key handler
                if event.code == sfml.Keyboard.ESCAPE:
                    return False
                elif event.code == sfml.Keyboard.LEFT:
                    self.game.horizontal -= 1
                elif event.code == sfml.Keyboard.RIGHT:
                    self.game.horizontal += 1
                elif event.code == sfml.Keyboard.UP:
                    self.game.vertical -= 1
                elif event.code == sfml.Keyboard.DOWN:
                    self.game.vertical += 1
                elif event.code == sfml.Keyboard.L_SHIFT:
                    print("HORIZONTAL OFFSET = " + str(self.game.horizontal))
                    print("VERTICAL OFFSET = " + str(self.game.vertical))
                    
        if self.window_focused:
            # handle input
            leftmouse = sfml.Mouse.is_button_pressed(sfml.Mouse.LEFT)
            mouse_x, mouse_y = sfml.Mouse.get_position(self.window)
        else:
            leftmouse = False
            mouse_x, mouse_y = (0,0)
        x = self.offsetx
        y = self.offsety
        hoveritem = None
        for item in self.menuitems:
            width, height = self.font.stringSize(item[0])
            # are we hovering over this item?
            if x <= mouse_x <= x+width and y <= mouse_y <= y+height:
                hoveritem = item
                if leftmouse and not self.prevleft and item[1]:
                    item[1](self)
            y += self.spacing
        self.prevleft = leftmouse
        
        # draw stuff
        self.draw(hoveritem)
        

        return True

# handler for main menu
class MainMenuHandler(MenuHandler):
    def item_start_game(self):
        self.manager.switch_handler(GameClientHandler)

    def item_go_github(self):
        webbrowser.open('http://github.com/PyGG2/PyGG2')

    def item_go_lobby(self):
        self.manager.switch_handler(LobbyHandler)

    def item_quit(self):
        self.manager.quit()

    menuitems = [
        ('Start test client', item_start_game),
        ('Lobby', item_go_lobby),
        ("Go to Github", item_go_github),
        ('Quit', item_quit)
    ]

    offsetx = 10
    offsety = 120
    spacing = 30

    def __init__(self, window, manager):
        super(MainMenuHandler, self).__init__(window, manager)

        self.menubg = sfml.Sprite(function.load_texture("gameelements/menubackgrounds/%s.png" % random.randint(0,2)))
        self.menubg.x = 200
        self.color = tuple(self.manager.config.setdefault('menu_color', [0.7, 0.25, 0]))
        self.color = sfml.Color(self.color[0] * 255, self.color[1] * 255, self.color[2] * 255)

    def draw(self, hoveritem):
        self.window.draw(self.menubg)
        rect = sfml.RectangleShape((200, 600))
        rect.fill_color = self.color
        self.window.draw(rect)

        super(MainMenuHandler, self).draw(hoveritem)

# handler for lobby
class LobbyHandler(MenuHandler):
    def go_back(self):
        self.manager.switch_handler(MainMenuHandler)

    offsetx = 210
    offsety = 120
    spacing = 30

    def __init__(self, window, manager):
        super(LobbyHandler, self).__init__(window, manager)

        self.menuitems = [
            ('Back to Main Menu', LobbyHandler.go_back),
            ('', None)
        ]

        self.menubg = sfml.Sprite(function.load_texture("gameelements/menubackgrounds/0.png"))
        self.menubg.x = 200
        self.menubg.x = 200
        self.color = tuple(self.manager.config.setdefault('menu_color', [0.7, 0.25, 0]))
        self.color = sfml.Color(self.color[0] * 255, self.color[1] * 255, self.color[2] * 255)

        self.sendbuf = b''

        self.lobbysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.num_servers = -1
        self.servers_read = 0

        self.lobbysocket.connect((constants.LOBBY_HOST, constants.LOBBY_PORT))
        lobbyuuid = uuid.UUID(constants.LOBBY_MESSAGE_TYPE_LIST).get_bytes()
        self.protocoluuid = uuid.UUID(constants.GG2_LOBBY_UUID).get_bytes()
        self.send_all(lobbyuuid+self.protocoluuid)

    def send_all(self, buf):
        while len(buf) > 0:
            sent = self.lobbysocket.send(buf)
            buf = buf[sent:]

    def recv_all(self, size):
        buf = b''
        while len(buf) < size:
            buf += self.lobbysocket.recv(size - len(buf))
        return buf
        #return self.lobbysocket.recv(size)

    def step(self):
        if self.num_servers == -1:
            num = self.recv_all(4)
            num = struct.unpack('>I', num)[0]
            self.num_servers = num
        elif self.servers_read < self.num_servers:
            length = self.recv_all(4)
            length = struct.unpack('>I', length)[0]
            if length > 100000:
                print('Server data block from lobby is too large')
                sys.exit(0)
            datablock = self.recv_all(length)
            server = {}
            items = struct.unpack('>BHBBBB18xHHHHH', datablock[:1+2+1+1+1+1+18+2+2+2+2+2])
            datablock = datablock[1+2+1+1+1+1+18+2+2+2+2+2:]
            server['protocol'], server['port'] = items[:2]
            server['ip'] = '.'.join([str(octet) for octet in items[2:6]])
            server['slots'], server['players'], server['bots'] = items[6:9]
            server['private'] = bool(items[9] & 1)
            infolen = items[10]
            server['infos'] = {}
            for i in range(infolen):
                keylen = struct.unpack('>B', datablock[0])[0]
                datablock = datablock[1:]
                key = datablock[:keylen]
                datablock = datablock[keylen:]
                datalen = struct.unpack('>H', datablock[:2])[0]
                datablock = datablock[2:]
                data = datablock[:datalen]
                datablock = datablock[datalen:]
                if key == 'protocol_id':
                    same_protocol_id = data == (self.protocoluuid)
                else:
                    server['infos'][key] = data
            server['compatible'] = (server['protocol'] == 0 and server['port'] > 0 and same_protocol_id)
            if server['bots']:
                playercount = '%s+%s' % (server['players'], server['bots'])
            else:
                playercount = str(server['players'])
            server['playerstring'] = '%s/%s' % (playercount, server['slots'])
            server['name'] = server['infos']['name']
            self.servers_read += 1

            self.menuitems.append( ('%s - [%s]' % (server['name'], server['playerstring']), None) )
        return super(LobbyHandler, self).step()

    def draw(self, hoveritem):
        self.window.draw(self.menubg)
        rect = sfml.RectangleShape((200, 600))
        rect.fill_color = self.color
        self.window.draw(rect)

        super(LobbyHandler, self).draw(hoveritem)
