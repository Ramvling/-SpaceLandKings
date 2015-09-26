import sys
### myo-raw imports
sys.path.insert(0, './myo-raw')
from  myo import *

### PyWebPlug imports
import string, cgi, time
sys.path.insert(0, './PyWebPlug')
from wsserver import *
from time import sleep

import pygame
from pygame.locals import *
import badgl
import level
from OpenGL.GL import *


clients = []
pID = 0
serverTurn = False
readyClients = []

def setupMessages():
    m1 = createMsgStruct(1, False)
    m1.addString()

    i1 = createMsgStruct(1, True)
    i1.addChars(2)

    test = createMsgStruct(2, False)
    test.addString()

    turn = createMsgStruct(3, True)
    turn.addChars(1)

    clientTurnOver = createMsgStruct(3, False)
    clientTurnOver.addChars(1)

    sendScore = createMsgStruct(4, True)
    sendScore.addString()

class Client:
    def __init__(self, socket, pID):
        self.socket = socket
        self.pID = pID
        self.position = [0, 0, 0]
        self.square = badgl.SquareObject(1.0, 1.0, badgl.loadImage("dragon.bmp"))
        self.square.z = 1
        self.diamondillium = 0

    def draw(self):
        self.square.x = self.position[0]
        self.square.y = self.position[1]
        self.square.z = self.position[2]
        self.square.draw()

    def handle(self, lvl):
        #send score update
        self.socket.newPacket(4)
        self.socket.write(str(self.diamondillium))
        self.socket.send()

        global pID
        if (self.socket.canHandleMsg() == False):
            return
        packet = self.socket.readPacket()
        msgID = packet.msgID
        if msgID == 1:
            name = packet.read()
            self.confirm()

        if msgID == 2:
            dirrections = packet.read().split(" ")
            for dirr in dirrections:
                if (dirr == "Forward"):
                    self.position[1] += 1
                elif (dirr == "Backward"):
                    self.position[1] += -1
                elif (dirr == "Right"):
                    self.position[0] += 1
                elif (dirr == "Left"):
                    self.position[0] -= 1
                elif (dirr == "Up"):
                    self.position[2] += 1
                elif (dirr == "Down"):
                    self.position[2] += -1
                lvl.events.runEvent(tuple(self.position), self)
            # since we don't need to do turn over naymore
            print("moving and appending to readyClients")
            readyClients.append(self)
            print(len(readyClients))
        if msgID == 3:
            print("messag id 3")
            readyClients.append(self)

    # Called to confirm to the client that the have been accepted, post sending us their details
    def confirm(self):
        self.socket.newPacket(1)
        self.socket.write(self.pID)
        self.socket.send()

    def disconnect(self):
        print("lost client")
        clients.remove(self)
        self.socket = None
        return

    def startTurn(self):
        self.socket.newPacket(3)
        self.socket.write('s')
        self.socket.send()
# this handles a new client
def handle(socket):
    global pID, clients
    pID += 1
    client = Client(socket, pID)
    clients.append(client)

class ServerPlayer:
    def __init__(self, moves, regen):
        self.x = 0
        self.y = 0
        self.z = 0
        self.moves = moves
        self.regen = regen
        self.square = badgl.SquareObject(1.0, 1.0, badgl.loadImage("king_face.bmp"))

    def draw(self):
        self.square.x = self.x
        self.square.y = self.y
        self.square.z = self.z
        self.square.draw()

myo_pos_change = 11

def main():
    global readyClients

    if len(readyClients) == len(clients):
        serverTurn = True;
        print("server turn");
    badgl.make_and_setup_window(800, 800)

    server_player = ServerPlayer(10, 10)
    server_player.z = 1

    lvl_size = 13
    lvl = level.Level(lvl_size, lvl_size)
    lvl.z = -0.1
    quit = False
    global myo_pos_change
    myo_pos_change = 0

    global gameStarted
    global stage
    using_myo = False
    if (len(sys.argv) > 1):
        using_myo = True
        m = Myo(NNClassifier(), None)
        def handle_myo(it):
            global myo_pos_change
            print("handling fo")
            print(it)
            if (it == 0):
                myo_pos_change = 0
            elif it == 1:
                myo_pos_change = 1
            elif it == 2:
                myo_pos_change = -1
            elif it == 3:
                myo_pos_change = 1
            elif it == 4:
                myo_pos_change = 1
            else:
                it = 0
            print(myo_pos_change)
        m.add_raw_pose_handler(handle_myo)
        m.connect()

    try:
        setupMessages()
        server = startServer()
        count = 0
        while not quit:
            for e in pygame.event.get():
                if e.type == QUIT:
                    quit = True
            newClient = handleNetwork()
            if newClient:
                handle(newClient)
                print("New connection")
            for client in clients:
                client.handle(lvl)

            if len(readyClients) == len(clients) and not serverTurn:
                serverTurn = True;
                print("server turn on in while");
                print(len(readyClients))

            if using_myo:
                myo_pos_change = 0
                m.run()
                if serverTurn:
                    server_player.x += myo_pos_change
                #print(myo_pos_change)
            #else:
            key_map = pygame.key.get_pressed()
            if key_map[K_ESCAPE]:
                quit = True
            if serverTurn and count > 10:
                if key_map[K_LEFT]:
                    server_player.x += -1
                    server_player.moves -=1
                    count = 0
                elif key_map[K_RIGHT]:
                    server_player.x += 1
                    server_player.moves -=1
                    count = 0
                elif key_map[K_UP]:
                    server_player.y += 1
                    server_player.moves -=1
                    count = 0
                elif key_map[K_DOWN]:
                    server_player.y -= 1
                    server_player.moves -=1
                    count = 0
                if key_map[K_SPACE] or server_player.moves <= 0:
                    print("end of server turn")
                    server_player.moves = server_player.regen
                    count = 0

                    serverTurn = False
                    for client in clients:
                        client.startTurn()
                    readyClients = []
                    print("at end of turn readyClients are")
                    print(readyClients)
            
            badgl.start_drawing()
            glTranslate(1, 1, -5)
            lvl.draw()
            for client in clients:
                client.draw()
            server_player.draw()
            badgl.end_drawing()
            #sleep(0.01)
            count += 1
            if (not count % 200):
                print(count)
    except KeyboardInterrupt:
        print(' recieved, closing server')
        server.close()
        raise

if __name__ == '__main__':
    main()




