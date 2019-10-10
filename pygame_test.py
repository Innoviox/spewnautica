import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import *
# import pyglet
import os
def load_object(name, **t):
    obj = OBJ(name, swapyz=True, transformations=Transformations.from_dict(t))
    return obj

class ObjectDict(dict):
    def __getattr__(self, item):
        return lambda **t: load_object(item, **t)

objects = ObjectDict()

class World:
    def __init__(self):
        self.world = []
        # self.batch = pyglet.graphics.Batch()
        self._setup()

    def _setup(self):
        obj = objects.fish()
        obj.scale(0.1, 0.1, 0.1)
        self.world.append(obj)
        self.world.append(objects.fish(translate=(5, 0, 0)))
        # self.batch

    def render(self):
        for obj in self.world:
            glCallList(obj.gl_list)

class Game:
    def __init__(self):
        pygame.init()
        self.viewport = (800, 600)
        self.hx = self.viewport[0] / 2
        self.hy = self.viewport[1] / 2
        self.srf = pygame.display.set_mode(self.viewport, OPENGL | DOUBLEBUF)
        self.clock = pygame.time.Clock()

        self._setup()
        self.world = World()

        self.rx, self.ry = (0, 0)
        self.tx, self.ty = (0, 0)
        self.zpos = 5
        self.rotate = self.move = False

    def _setup(self):
        # Call a bunch of OpenGL methods.
        glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width, height = self.viewport
        gluPerspective(90.0, width / float(height), 1, 100.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)
        glClearColor(0.5, 0.69, 1.0, 1)
        glEnable(GL_CULL_FACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def handle_input(self, e):
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: self.zpos = max(1, self.zpos-1)
            elif e.button == 5: self.zpos += 1
            elif e.button == 1: self.rotate = True
            elif e.button == 3: self.move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: self.rotate = False
            elif e.button == 3: self.move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if self.rotate:
                self.rx += i
                self.ry += j
            if self.move:
                self.tx += i
                self.ty -= j

    def tick(self):
        self.clock.tick(30)
        for e in pygame.event.get():
            self.handle_input(e)
        self.draw()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslate(self.tx / 20., self.ty / 20., - self.zpos)
        glRotate(self.ry, 1, 0, 0)
        glRotate(self.rx, 0, 1, 0)
        # glCallList(obj.gl_list)

        self.world.render()

        pygame.display.flip()

    def loop(self):
        while 1:
            self.tick()

if __name__ == "__main__":
    game = Game()
    game.loop()