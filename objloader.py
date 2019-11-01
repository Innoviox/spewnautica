import pygame
from OpenGL.GL import *
import lib_euclid as euclid
import math
import builtins
map = lambda a, b: list(builtins.map(a, b)) # fix python 2 map
from pyglet import image
# from pyglet.gl import *
from pyglet.graphics import TextureGroup

def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError("mtl file doesn't start with newmtl stmt")
        elif values[0] == 'map_Kd':
            # load the texture referred to by this declaration
            mtl[values[0]] = values[1]
            surf = pygame.image.load(mtl['map_Kd'])
            image = pygame.image.tostring(surf, 'RGBA', 1)
            ix, iy = surf.get_rect().size
            texid = mtl['texture_Kd'] = glGenTextures(1)
            contents['map_Kd'] = mtl['map_Kd']
            glBindTexture(GL_TEXTURE_2D, texid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, ix, iy, 0, GL_RGBA,
                GL_UNSIGNED_BYTE, image)
        else:
            mtl[values[0]] = map(float, values[1:])
    return contents

def load_texture():
    surf = pygame.image.load("assets/texture.png")
    image = pygame.image.tostring(surf, 'RGB', 1)
    ix, iy = surf.get_rect().size
    texture_image = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_image)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
        GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
        GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, ix, iy, 0, GL_RGB,
        GL_UNSIGNED_BYTE, image)
    return texture_image



class Transformations:
    def __init__(self):
        self.transforms = euclid.Matrix4.new_identity()
        self.translation = 0, 0, 0
        self.rotation = []
        self._scale = 1, 1, 1
        self.mtl = None

    def translate(self, x, y, z):
        self.transforms.translate(x, y, z)
        a, b, c = self.translation
        self.translation = (a + x, b + y, c + z)
        return self

    def rotate(self, angle, x, y, z):
        self.transforms.rotate_axis(math.pi*angle/180.0, euclid.Vector3(x, y, z))
        self.rotation.append((angle, x, y, z))
        return self

    def scale(self, x, y, z):
        self.transforms.scale(x, y, z)
        a, b, c = self._scale
        self._scale = (a * x, b * y, c * z)
        return self

    def texture(self, *t):
        mtl = list(t)
        self.mtl =[]
        for i in range(0, len(mtl), 2):
            self.mtl.append([mtl[i], mtl[i+1]])
        return self

    def _do(self, s, *args):
        getattr(self, s)(*args)

    @classmethod
    def from_dict(cls, d: dict):
        t = cls()
        for tr, vals in d.items():
            t._do(tr, *vals)
        return t

import os
TEX = None
groups = {}
class OBJ:
    __cache__ = {}

    def __init__(self, name, swapyz=False, transformations=Transformations()):
        """Loads a Wavefront OBJ file. """
        global TEX
        if not TEX:
            TEX = load_texture()
            groups['cube'] = TextureGroup(image.load("assets/texture.png").get_texture())

        self._fn, self._s = name, swapyz
        self.transformations = transformations
        if name in OBJ.__cache__:
            self.vertices, self.normals, self.texcoords, self.faces = OBJ.__cache__[name]
            self.group = groups[name]
        else:
            os.chdir(f"assets/models/{name}/obj")
            file = open(f"{name}.obj", "r")

            self.vertices = []
            self.normals = []
            self.texcoords = []
            self.faces = []

            material = None
            for line in file:
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'v':
                    v = map(float, values[1:4])
                    if swapyz:
                        v = v[0], v[2], v[1]
                    x, y, z = v
                    # v = list(self.transformations.transforms * euclid.Point3(x, y, z))
                    self.vertices.append(v)
                elif values[0] == 'vn':
                    v = map(float, values[1:4])
                    if swapyz:
                        v = v[0], v[2], v[1]
                    x, y, z = v
                    # v = list(self.transformations.transforms * euclid.Point3(x, y, z))
                    self.normals.append(v)
                elif values[0] == 'vt':
                    self.texcoords.append(map(float, values[1:3]))
                elif values[0] in ('usemtl', 'usemat'):
                    material = values[1]
                elif values[0] == 'mtllib':
                    self.mtl = MTL(values[1])
                elif values[0] == 'f':
                    face = []
                    texcoords = []
                    norms = []
                    for v in values[1:]:
                        w = v.split('/')
                        face.append(int(w[0]))
                        if len(w) >= 2 and len(w[1]) > 0:
                            texcoords.append(int(w[1]))
                        else:
                            texcoords.append(0)
                        if len(w) >= 3 and len(w[2]) > 0:
                            norms.append(int(w[2]))
                        else:
                            norms.append(0)
                    self.faces.append((face, norms, texcoords, material))
            if material:
                groups[name] = self.group = TextureGroup(image.load(self.mtl['map_Kd']).get_texture())
            elif name == 'cube':
                self.group = groups['cube']
            os.chdir("../../../../")
            OBJ.__cache__[name] = (self.vertices[:], self.normals[:], self.texcoords[:], self.faces[:])

        if False:
            self.gl_list = glGenLists(1)
            glNewList(self.gl_list, GL_COMPILE)
            glEnable(GL_TEXTURE_2D)
            glFrontFace(GL_CCW)
            for face in self.faces:
                vertices, normals, texture_coords, material = face
                try:
                    mtl = self.mtl[material]
                except AttributeError:
                    mtl = {'texture_Kd': TEX}
                if 'texture_Kd' in mtl:
                    # use diffuse texmap
                    glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
                # else:
                    # just use diffuse colour
                #     glColor(*mtl['Kd'])
                elif 'Kd' in mtl:
                    glColor(*mtl['Kd'])

                glBegin(GL_POLYGON)
                for i in range(len(vertices)):
                    if normals[i] > 0:
                        glNormal3fv(self.normals[normals[i] - 1])
                    if texture_coords[i] > 0:
                        glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                    glVertex3fv(self.vertices[vertices[i] - 1])
                glEnd()
            glDisable(GL_TEXTURE_2D)
            glEndList()

    def add(self, batch):
        # if self._fn == 'cube': #len(self.vertices[0]) == 3:
        typ = GL_QUADS
        # else:
        #     typ = GL_TRIANGLES
        if self.transformations.mtl:
            self.texcoords = self.transformations.mtl
        self.vertices = map(lambda i: list(self.transformations.transforms * euclid.Point3(i[0], i[1], i[2])), self.vertices)
        self.normals = map(lambda i: list(self.transformations.transforms * euclid.Point3(i[0], i[1], i[2])), self.normals)

        for face in self.faces:
            _verts, norms, texc, mat = face
            verts = [self.vertices[i - 1] for i in _verts]
            texc = [self.texcoords[i - 1] for i in texc]
            ex_verts = [i for v in verts for i in v]
            batch.add(len(ex_verts) // 3,
              typ,
              self.group,
              ('v3f/static', tuple(ex_verts)),
              # ('n3f/static', tuple([i for n in self.normals for i in n])),
              ('t2f/static', tuple([i for t in texc for i in t])),
              )

    def _reinit(self):
        self.__init__(self._fn, self._s, self.transformations)

    def scale(self, *a):
        self.transformations._do('scale', *a)
        self._reinit()
        return self

    def rotate(self, *a):
        self.transformations._do('rotate', *a)
        self._reinit()
        return self

    def translate(self, *a):
        self.transformations._do('translate', *a)
        self._reinit()
        return self

    def texture(self, t):
        self.transformations._do('texture', t)
        self._reinit()
        return self

    def apply_transforms(self, ts):
        for a, b in ts.items():
            self.transformations._do(a, *b)
        self._reinit()
        return self


