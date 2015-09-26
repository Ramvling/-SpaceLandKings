import badgl
from OpenGL.GL import *

class Level:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.square = badgl.SquareObject(1.0, 1.0, badgl.loadImage("single_tile.bmp"))

    def draw(self):
        for x in range(-self.width//2, self.width//2):
            for y in range(-self.height//2, self.height//2):
                glTranslate(x, y, 0)
                self.square.draw()
                glTranslate(-x, -y, 0)



