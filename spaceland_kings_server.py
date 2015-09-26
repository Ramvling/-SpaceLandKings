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

def setupMessages():
    m1 = createMsgStruct(1, False)
    m1.addString()

    i1 = createMsgStruct(1, True)
    i1.addChars(2)

    test = createMsgStruct(2, False)
    test.addString()

    testOut = createMsgStruct(2, True)
    testOut.addString()

class Client:
    def __init__(self, socket, pID):
        self.socket = socket
        self.pID = pID

    def handle(self):
        global pID
        if (self.socket.canHandleMsg() == False):
            return
        packet = self.socket.readPacket()
        msgID = packet.msgID
        if msgID == 1:
            name = packet.read()
            self.confirm()

        if msgID == 2:
            print(packet.read())
            self.socket.newPacket(2)
            self.socket.write("Hello from the server")
            self.socket.send()
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

# this handles a new client
def handle(socket):
    global pID, clients
    pID += 1
    client = Client(socket, pID)
    clients.append(client)

myo_pos_change = 11

def main():
    badgl.make_and_setup_window(800, 800)

    square = badgl.SquareObject(1.0, 1.0, badgl.loadImage("king_face.png"))
    square.z = 1
    lvl_size = 13
    lvl = level.Level(lvl_size, lvl_size)
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
                client.handle()
            if using_myo:
                myo_pos_change = 0
                m.run()
                square.x += myo_pos_change
                #print(myo_pos_change)
            #else:
            key_map = pygame.key.get_pressed()
            if key_map[K_LEFT]:
                square.x += -1
            elif key_map[K_RIGHT]:
                square.x += 1
            elif key_map[K_UP]:
                square.y += 1
            elif key_map[K_DOWN]:
                square.y -= 1
            elif key_map[K_ESCAPE]:
                quit = True
            
            badgl.start_drawing()
            glTranslate(1, 1, -5)
            lvl.draw()
            square.draw()
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




