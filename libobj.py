import os
import pickle
import types

from OpenGL.GL import *

class Point(object):

    def __init__(self, x, y, z, n=None):
        self.x = x
        self.y = y
        self.z = z
        self.n = n

    def pp(self):
        return (self.x, self.y, self.z)

    def run_gl(self):
        if self.n:
            glNormal3f(*self.n)
        pp = self.pp()
        glVertex3f(*pp)

    def __repr__(self):
        coords = 'Point: %5.2f, %5.2f, %5.2f' % self.pp()
        if self.n is not None:
            return '%s [n=%s]' % (coords, ', '.join(map(
                lambda x: '%5.2f' % (x), self.n)))
        else:
            return coords

    def __str__(self):
        return self.__repr__()

class Triangle(object):
    def __init__(self, i1, i2, i3, n):
        self.i1 = i1
        self.i2 = i2
        self.i3 = i3
        self.n = n

    def points(self):
        return [self.i1, self.i2, self.i3]

    def run_gl(self):
        glNormal3f(*self.n)

class Poly(object):
    def __init__(self, indices):
        self.indices = indices

    def __repr__(self):
        return "Poly: [%s]" % (', '.join(map(str, self.indices)))

    def __str__(self):
        return self.__repr__()

class Object(object):

    def __init__(self, data=None):
        if data is not None:
            self.load(data)

    def load_from_file(self, fn):
        self.data = pickle.loads(open(fn, 'rb').read())

    def load(self, data):
        if type(data) == types.StringType and os.path.isfile(data):
            self.load_from_file(data)
        elif type(data) == types.DictType:
            self.data = data

    def save_to_file(self, fn):
        open(fn, 'wb').write(pickle.dumps(self.data, 2))

    def get_points(self):
        return self.data['points']

    def get_triangles(self):
        return self.data.get('triangles', [])

    def get_polys(self):
        return self.data.get('polys', [])

    def set_points(self, points):
        if not hasattr(self, 'data'):
            self.data = {}

        self.data['points'] = points

    def set_triangles(self, triangles):
        if not hasattr(self, 'data'):
            self.data = {}

        self.data['triangles'] = triangles

    def set_polys(self, polys):
        if not hasattr(self, 'data'):
            self.data = {}

        self.data['polys'] = polys

    def run_gl(self):
        points = self.get_points()
        triangles = self.get_triangles()
        polys = self.get_polys()

        if triangles:
            glBegin(GL_TRIANGLES)
            for t in triangles:
                for i in t.points():
                    points[i].run_gl()
                    t.run_gl()
            glEnd()

        if polys:
            for p in polys:
                glBegin(GL_POLYGON)
                for i in p.indices:
                    points[i].run_gl()
                glEnd()

"""
    Nx = UyVz - UzVy
    Ny = UzVx - UxVz
    Nz = UxVy - UyVx
"""
def triangle_normal(p1, p2, p3):
    ux = p2.x - p1.x
    uy = p2.y - p1.y
    uz = p2.z - p1.z

    vx = p3.x - p1.x
    vy = p3.y - p1.y
    vz = p3.z - p1.z

    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx

    return (nx, ny, nz, )
