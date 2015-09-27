from ctypes import *
import sys
import pygame
from pygame.locals import *

#try:
    ## for OpenGL ctypes, apparently
    #from OpenGL import platform
    #gl = platform.OpenGL
#except ImportError:
try:
    # for PyOpenGL, apparently
    gl = cdll.LoadLibrary('libGL.so')
except OSError:
    # for mac
    from ctypes.util import find_library
    # get absolute path to framework
    path = find_library('OpenGL')
    gl = cdll.LoadLibrary(path)

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


glCreateShader = gl.glCreateShader
glShaderSource = gl.glShaderSource
glShaderSource.argtypes = [c_int, c_int, POINTER(c_char_p), POINTER(c_int)]
#glShaderSource.argtypes = [c_int, c_int, POINTER(c_wchar_p), POINTER(c_int)]
glCompileShader = gl.glCompileShader
glGetShaderiv = gl.glGetShaderiv
glGetShaderiv.argtypes = [c_int, c_int, POINTER(c_int)]
glGetShaderInfoLog = gl.glGetShaderInfoLog
glGetShaderInfoLog.argtypes = [c_int, c_int, POINTER(c_int), c_char_p]
glDeleteShader = gl.glDeleteShader
glCreateProgram = gl.glCreateProgram
glAttachShader = gl.glAttachShader
glLinkProgram = gl.glLinkProgram
glGetError = gl.glGetError
glUseProgram = gl.glUseProgram

GL_FRAGMENT_SHADER  = 0x8B30
GL_VERTEX_SHADER    = 0x8B31
GL_COMPILE_STATUS   = 0x8B81
GL_LINK_STATUS      = 0x8B82
GL_INFO_LOG_LENGTH  = 0x8B84

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    length = c_int(len(source))
    source = c_char_p(bytes(source, 'utf-8'))
    #source = c_wchar_p(source)
    #length = c_int(-1)
    glShaderSource(shader, 1, byref(source), byref(length))
    glCompileShader(shader)

    status = c_int()
    glGetShaderiv(shader, GL_COMPILE_STATUS, byref(status))
    if not status.value:
        print_log(shader)
        glDeleteShader(shader)
        raise ValueError('shader comp failed')
    return shader

def compile_program(vertex_source, fragment_source):
    vertex_shader = None
    fragment_shader = None
    program = glCreateProgram()

    if vertex_source:
        vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
        glAttachShader(program, vertex_shader)
    if fragment_source:
        fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
        glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if vertex_shader:
        glDeleteShader(vertex_shader)
    if fragment_shader:
        glDeleteShader(fragment_shader)

    return program

def print_log(shader):
    length = c_int()
    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, byref(length))
 
    if length.value > 0:
        log = create_string_buffer(length.value)
        glGetShaderInfoLog(shader, length, byref(length), log)
        print ("printing log:")
        print (log.value)
        print ("done printing log")

def createDL(width, height, program, texture):
    newList = glGenLists(1)
    glNewList(newList, GL_COMPILE)
    glBindTexture(GL_TEXTURE_2D, texture)
    #glUseProgram(program)
    glBegin(GL_QUADS)

    #bottom left
    glTexCoord2f(0,0); glVertex2f(0,0);
    #top left
    glTexCoord2f(0,1); glVertex2f(0,height);
    #top right
    glTexCoord2f(1,1); glVertex2f(width,height);
    #bottom right
    glTexCoord2f(1,0); glVertex2f(width,0);
    glEnd()
    glEndList()
    return newList

def make_and_setup_window(width, height):
    glutInit(sys.argv)
    pygame.init()
    pygame.display.set_mode((width, height), OPENGL | DOUBLEBUF)

    # maybe the below needs more. whatever
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90.0, width/float(height), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    #texturing
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

angle = 0
angle_delta = 0.10
def start_drawing():
    global angle
    global angle_delta
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslate(0.0, 5.0, -4.0)
    angle += angle_delta
    #if angle > 60 or angle < -60:
    if angle > 20 or angle < -20:
        angle_delta = -angle_delta
    glRotate(-35, 1.0, 0.0, 0.0)
    #glRotate(angle, 1.0, 0.0, 0.0)
    glRotate(angle, 0.0, 0.0, 1.0)

def end_drawing():
    pygame.display.flip()

class SquareObject:
    def __init__(self, width, height, texture):
        self.program = compile_program('''
        // Vertex program
        varying vec3 pos;
        void main() {
            pos = gl_Vertex.xyz;
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }
        ''', '''
        // Fragment program
        //uniform sampler2D tex;
        varying vec3 pos;
        void main() {
            gl_FragColor.rgb = pos.xyz;
            //gl_FragColor.rgb = gl_FragColor.rgb * pos.xyz;
            //gl_FragColor.rgb = texture2D(tex, gl_TexCoord[0].st).rgb;
        }
        ''')

        self.draw_list = createDL(width, height, self.program, texture)
        self.x = 0
        self.y = 0
        self.z = 0

    def draw(self):
        glTranslate(self.x, self.y, self.z)
        glCallList(self.draw_list)
        glTranslate(-self.x, -self.y, -self.z)

def loadImage(path):
    tex_surface = pygame.image.load(path)
    tex_data = pygame.image.tostring(tex_surface, "RGBA", 1)
    width = tex_surface.get_width()
    height = tex_surface.get_height()
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
    return texture

def drawText(position, string):
    font = pygame.font.Font(None, 32)
    text_surface = font.render(string, True, (255,255,255,255), (0,0,0,255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

if __name__ == '__main__':

    make_and_setup_window(640, 480)
    square = SquareObject(1.5, 1.5, loadImage("single_tile.png"))

    quit = False
    x_pos = 0
    while not quit:
        for e in pygame.event.get():
            if e.type in (QUIT, KEYDOWN):
                quit = True
        x_pos += 0.01
        square.x = x_pos
        square.y = x_pos
        square.z = x_pos
        start_drawing()
        square.draw()
        end_drawing()
        pygame.time.wait(1)

