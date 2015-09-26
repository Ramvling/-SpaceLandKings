import badgl
from  events import *
from OpenGL.GL import *
import random

class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.z = 0
        self.regular_square = badgl.SquareObject(1.0, 1.0, badgl.loadImage("single_tile.bmp"))
        self.diamondillium_square = badgl.SquareObject(1.0, 1.0, badgl.loadImage("diamondillium.bmp"))

        diamondillium_pos = [(random.randrange(-width//2, width//2), random.randrange(-height//2, height//2),0) for i in range(5)]
        #diamondillium_pos = [(0,0,0), (1,1,1)]
        #print("the pos")
        #for i in diamondillium_pos:
            #print(i)
        self.special_positions = {}

        for pos in diamondillium_pos:
            self.special_positions[pos] = self.diamondillium_square

        # so we can reference in the closure
        self.events = None
        def increment_dimondillium(client):
            client.diamondillium += 1
            print("incremented client dimondillum to")
            print(client.diamondillium)
            del self.special_positions[tuple(client.position)]
            del self.events.positions[tuple(client.position)]
            # sketchy since we don't modify the event the position array was generated from
            #del self.events.eventpositions[tuple(client.position)]

        self.events = EventManager([Event("diamondillium", diamondillium_pos, increment_dimondillium)])

    def draw(self):
        for x in range(-self.width//2, self.width//2):
            for y in range(-self.height//2, self.height//2):
                if ((x,y,0) not in self.special_positions):
                    glTranslate(self.x + x, self.y + y, self.z)
                    self.regular_square.draw()
                    glTranslate(-(self.x + x), -(self.y + y), -self.z)
        for special in self.special_positions:
            glTranslate(self.x + special[0], self.y + special[1], self.z + special[2])
            self.special_positions[special].draw()
            glTranslate(-(self.x + special[0]), -(self.y + special[1]), -(self.z + special[2]))




