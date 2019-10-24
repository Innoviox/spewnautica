import sys, pygame
# from pygame.locals import *
from pygame.constants import *
# from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import *
import lib as lib3d
# from OpenGL.raw.GL.NV import occlusion_query as ou
import pyglet
import time
# import os
import random

GRASS, *_, SAND, BRICK, STONE = lib3d.make_3d_textures(3, 2, special={0: (2, 1, 0)})
texture_dict = dict(zip('gsbo', (GRASS, SAND, BRICK, STONE)))
TICKS_PER_SEC = 60
def load_object(name, **t):
    obj = OBJ(name, swapyz=True, transformations=Transformations.from_dict(t))
    return obj

class ObjectDict(dict):
    def __getattr__(self, item):
        return lambda **t: load_object(item, **t)

objects = ObjectDict()
objmap = {
    'f': 'fish',
    '2': 'fish2',
    'n': 'nemo',
    't': 'tang',
    'c': 'crab-eating-frog',
    'm': 'megalodon'
}

obj_transform_map = {
    'n': {
        'scale': (0.1, 0.1, 0.1),
        'rotate': (90, 2, 1, 1)
    },
    't': {
        'scale': (0.2, 0.2, 0.2),
        'rotate': (90, 1, 0, 0)
    },
    'c': {
        'scale': (0.2, 0.2, 0.2)
    }
}

def get_object(s):
    if s in 'gsbo':
        return objects.cube(texture=texture_dict[s])
    elif s in objmap:
        return getattr(objects, objmap[s])().apply_transforms(obj_transform_map.get(s, {}))

    print(s)

class World:
    def __init__(self, file):
        self.world = []
        self.queue = []
        self.batch = pyglet.graphics.Batch()
        self.render = self.batch.draw

        self._initialize_from_file(file)
        # self._setup()

    def _initialize_from_file(self, file):
        size, *lines = map(str.strip, open(file))
        # sx, sy, sz = map(int, size.split("x"))
        cx = cy = cz = 0

        for line in lines:
            if line == "-":
                cx = cy = 0
                cz += 1
                continue
            for char in line:
                if char == ':':   continue
                elif char == ' ': pass
                elif char == 'C': break
                else: self.add_obj(get_object(char).translate(cx, cy, cz))
                cy += 1
            cy = 0
            cx += 1

    def _add(self, obj):
        def __add():
            obj.add(self.batch)
            self.world.append(lib3d.normalize(obj.vertices[0]))
            print(lib3d.normalize(obj.vertices[0]))
        return __add

    def add_block(self, pos, texture, immediate):
        """
        Compatibility method for interacting with pylib3d
        """
        self.queue.append(self._add(objects.cube(texture=texture, translate=pos)))

    def add_obj(self, obj):
        # self.queue.append(lambda: self.world.append(obj))
        self.queue.append(self._add(obj))
        # self.dequeue()
        # self.batch.add()

    def dequeue(self, n=1):
        while self.queue and n > 0:
            self.queue.pop(0)()
            n -= 1

    def empty_queue(self):
        self.dequeue(n=len(self.queue))

    def process_queue(self):
        start = time.perf_counter()
        while self.queue and time.perf_counter() - start < 1.0 / TICKS_PER_SEC:
            self.dequeue()

    # def render(self):
    #     glCallLists([i.gl_list for i in self.world])
        # for obj in self.world:
        #     glCallList(obj.gl_list)



class Game:
    def __init__(self):
        pygame.init()
        self.viewport = (800, 600)
        self.hx = self.viewport[0] / 2
        self.hy = self.viewport[1] / 2
        self.srf = pygame.display.set_mode(self.viewport, OPENGL | DOUBLEBUF)
        self.clock = pygame.time.Clock()

        self._setup()
        self.world = World(file="test_file.txt")

        self.rx, self.ry = (0, 0)
        self.tx, self.ty = (0, 0)
        self.zpos = 0
        self.rotate = self.move = False

        pyglet.clock.schedule_interval(self.tick, 1.0 / TICKS_PER_SEC)

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
        # glEnable(GL_CULL_FACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def handle_input(self, e):
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
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
                self.tx += i * 20
                self.ty -= j * 20

    def handle_keys(self, keys):
        if keys[K_w]:
            self.zpos -= 10
        if keys[K_a]:
            self.tx += 10
        if keys[K_s]:
            self.zpos += 10
        if keys[K_d]:
            self.tx -= 10

    def tick(self):
        # self.clock.tick(30)
        self.world.process_queue()
        for e in pygame.event.get():
            self.handle_input(e)
        self.handle_keys(pygame.key.get_pressed())
        self.collide()
        self.draw()

    def collide(self):
        pad = 0.25
        pos = [self.tx / 20, self.ty / 20, self.zpos / 20]
        np = lib3d.normalize(pos)
        for face in lib3d.FACES:
            for i in range(3):
                if not face[i]:
                    continue

                d = (pos[i] - np[i]) * face[i]
                if d < pad:
                    continue

                for dy in range(2):
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.world.world:
                        continue
                    print('a')
                    pos[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        self.dy = 0
                    break
        self.tx, self.ty, self.zpos = (pos[0] * 20, pos[1] * 20, pos[2] * 20)


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslate(self.tx / 20., self.ty / 20., - self.zpos / 20.)
        glRotate(self.ry, 1, 0, 0)
        glRotate(self.rx, 0, 1, 0)

        self.world.render()

        pygame.display.flip()

    def loop(self):
        while 1:
            self.tick()

if __name__ == "__main__":
    game = Game()
    game.loop()