import sys
### myo-raw imports
sys.path.insert(0, './myo-raw')
from  myo import *

### PyWebPlug imports
import string, cgi, time
sys.path.insert(0, './PyWebPlug')
from wsserver import *
from time import sleep


clients = []
pID = 0

def setupMessages():
    m1 = createMsgStruct(1, False)
    m1.addString()

    i1 = createMsgStruct(1, True)
    i1.addChars(2)

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

def main():
    global gameStarted
    global stage
    m = Myo(NNClassifier(), None)
    def handle_myo(it):
        print("handling fo")
        print(it)
    m.add_raw_pose_handler(handle_myo)
    m.connect()

    try:
        setupMessages()
        server = startServer()
        while True:
            newClient = handleNetwork()
            if newClient:
                handle(newClient)
                print("New connection")
            for client in clients:
                client.handle()
            m.run()
            #sleep(0.01)
    except KeyboardInterrupt:
        print(' recieved, closing server')
        server.close()

if __name__ == '__main__':
    main()




