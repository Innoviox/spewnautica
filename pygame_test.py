import sys, pygame
# from pygame.locals import *
from pygame.constants import *
# from OpenGL.GL import *
from OpenGL.GLU import *
from objloader import *
from lib import make_3d_textures
# from OpenGL.raw.GL.NV import occlusion_query as ou
import pyglet
import time
# import os
import random
GRASS, *_, SAND, BRICK, STONE = make_3d_textures(3, 2, special={0: (2, 1, 0)})
texture_dict = dict(zip('gsbo', (GRASS, SAND, BRICK, STONE)))
TICKS_PER_SEC = 60
def load_object(name, **t):
    obj = OBJ(name, swapyz=True, transformations=Transformations.from_dict(t))
    return obj

class ObjectDict(dict):
    def __getattr__(self, item):
        return lambda **t: load_object(item, **t)


objects = ObjectDict()



def get_object(s):
    if s in 'gsbo':
        return objects.cube(texture=texture_dict[s])
    elif s == 'f':
        return objects.fish()
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
        sx, sy, sz = map(int, size.split("x"))
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


    def _setup(self):
        # for i, t in zip(range(4), [GRASS, SAND, BRICK, STONE]):
        #     cube = objects.cube(texture=t, translate=(i, 0, 0))
        #     self.add_obj(cube)

        self.add_obj(objects.fish())

        # obj.translate(5, 0, 0)
        # obj.scale(0.1, 0.1, 0.1)
        # obj.rotate(90, 0, 0, 1)
        # self.world.append(obj)
        # self.world.append(objects.fish(scale=(0.1,0.1,0.1)))
        # self.batch
        n = 80  # 1/2 wid€th and height of world
        s = 1  # step size
        y = 0  # initial y height
        z = 0
        for x in range(-n, n + 1, s):
            # print(x)
            for y in range(-n, n + 1, s):
                # create a layer stone an grass everywhere.
                self.add_obj(objects.cube(texture=GRASS, translate=(x, y, z)))
                self.add_obj(objects.cube(texture=GRASS, translate=(x, y, z - 1)))
                # if x in (-n, n) or z in (-n, n):
                #     # create outer walls.
                #     for dy in range(-2, 3):
                #         self.world.append(objects.cube(texture=STONE, translate=(x, y + dy, z)))

        # # generate the hills randomly
        o = n - 10
        for _ in range(120):
            # print(_)
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(1, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice([GRASS, SAND, BRICK])
            for y in range(c, c + h):
                for x in range(a - s, a + s + 1):
                    for z in range(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        # self.add_block((x, y, z), t, immediate=False)
                        self.add_obj(objects.cube(texture=t, translate=(x, z, y)))
                s -= d  # decrement side length so hills taper off
        print("initialized")

    def add_obj(self, obj):
        # self.queue.append(lambda: self.world.append(obj))
        self.queue.append(lambda:obj.add(self.batch))
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
        self.draw()

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