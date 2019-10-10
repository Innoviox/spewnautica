import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import *

import os
def load_object(name):
    os.chdir(f"assets/models/{name}/obj")
    obj = OBJ(f"{name}.obj", swapyz=True)
    os.chdir("../../../../")
    return obj

class ObjectDict(dict):
    def __getattr__(self, item):
        if item in self:
            return self[item] # improve performance by caching result
        obj = load_object(item)
        self[item] = obj
        return obj

objects = ObjectDict()

class World:
    def __init__(self):
        self.world = []
        self._setup()

    def _setup(self):
        self.world.append(objects.fish)

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
        glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width, height = self.viewport
        gluPerspective(90.0, width / float(height), 1, 100.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)


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