import badgl
from  events import *
from OpenGL.GL import *

class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.z = 0
        self.square = badgl.SquareObject(1.0, 1.0, badgl.loadImage("single_tile.bmp"))
        def increment_dimondillium(client):
            client.diamondillium += 1
            print("incremented client dimondillum to")
            print(client.diamondillium)

        self.events = EventManager([Event("random diamondillium", [(0,0,0)], increment_dimondillium)])

    def draw(self):
        for x in range(-self.width//2, self.width//2):
            for y in range(-self.height//2, self.height//2):
                glTranslate(self.x + x, self.y + y, self.z)
                self.square.draw()
                glTranslate(-(self.x + x), -(self.y + y), -self.z)



