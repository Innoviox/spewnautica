import pygame
from OpenGL.GL import *
import lib_euclid as euclid
import math
import builtins
map = lambda a, b: list(builtins.map(a, b)) # fix python 2 map


def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        # print(values)
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
        self.mtl = None

    def translate(self, x, y, z):
        self.transforms.translate(x, y, z)
        return self

    def rotate(self, angle, x, y, z):
        self.transforms.rotate_axis(math.pi*angle/180.0, euclid.Vector3(x, y, z))
        return self

    def scale(self, x, y, z):
        self.transforms.scale(x, y, z)
        self.normalize = True
        return self

    def texture(self, *t):
        mtl = list(t)
        print(mtl)
        self.mtl =[]
        for i in range(0, len(mtl), 2):
            self.mtl.append([mtl[i], mtl[i+1]])
        print(self.mtl)
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
class OBJ:
    def __init__(self, name, swapyz=False, transformations=Transformations()):
        """Loads a Wavefront OBJ file. """
        os.chdir(f"assets/models/{name}/obj")
        filename = f"{name}.obj"
        self.__fn, self.__s = name, swapyz

        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        self.transformations = transformations

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                x, y, z = v
                v = list(self.transformations.transforms * euclid.Point3(x, y, z))
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                x, y, z = v
                v = list(self.transformations.transforms * euclid.Point3(x, y, z))
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
        if transformations.mtl:
            self.texcoords = transformations.mtl
        os.chdir("../../../../")
        texture_image = load_texture()

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            try:
                mtl = self.mtl[material]
            except AttributeError:
                mtl = {'texture_Kd': texture_image}
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
                    print("HI", self.texcoords[texture_coords[i] - 1])
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()



    def _reinit(self):
        self.__init__(self.__fn, self.__s, self.transformations)

    def scale(self, *a):
        self.transformations._do('scale', *a)
        self._reinit()

    def rotate(self, *a):
        self.transformations._do('rotate', *a)
        self._reinit()

    def translate(self, *a):
        self.transformations._do('translate', *a)
        self._reinit()

    def texture(self, t):
        self.transformations._do('texture', t)
        self._reinit()



