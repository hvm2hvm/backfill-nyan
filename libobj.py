import os
import pickle
import types

from OpenGL.GL import *

try:
    import numpy
    from stl import mesh
except ImportError:
    numpy = None
    mesh = None

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

    def __add__(self, other):
        if type(other) in [int, float]:
            return Point(self.x + other, self.y + other, self.z + other)
        elif type(other) == Point:
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if type(other) in [int, float]:
            return Point(self.x - other, self.y - other, self.z - other)
        elif type(other) == Point:
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if type(other) in [int, float]:
            return Point(self.x * other, self.y * other, self.z * other)
        elif type(other) == Point:
            return self.dot(other)

    def __pow__(self, other):
        if type(other) in [int, float]:
            return Point(self.x ** other, self.y ** other, self.z ** other)
        elif type(other) == Point:
            return self.cross(other)
        
    def __div__(self, other):
        if type(other) in [int, float]:
            return Point(self.x / other, self.y / other, self.z / other)
        else:
            raise NotImplemented("Point: div: can only divide with scalars")

    def __neg__(self):
        return Point(-self.x, -self.y, -self.z)
    
    def dist_to(self, other):
        s = self-other
        return s.dot(s) ** 0.5

    def cross(self, other):
        return Point(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

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

        self.process()

    def process(self):
        self.min = [None, ] * 3
        self.max = [None, ] * 3
        for p in self.get_points():
            p = p.pp()
            for i in range(3):
                if self.min[i] is None or p[i] < self.min[i]:
                    self.min[i] = p[i]
                if self.max[i] is None or p[i] > self.max[i]:
                    self.max[i] = p[i]

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

# TODO: make a standard "save to file" object that can hold information about what it is
# TODO: i.e. is it a scene or an object - a loader method/function would then look at that
# TODO: and load as scene or object automatically. Maybe use a parameter like replace_scene
class Scene(object):

    def __init__(self, data=None):
        if type(data) == str:
            self.load_from_file(data)
        elif type(data) == list:
            self.objects = data
        else:
            self.objects = []

    def add_object(self, object):
        self.objects.append(object)

    def load_from_file(self, filename):
        self.objects = pickle.loads(open(filename, 'rb').read())

        for o in self.objects:
            o.process()

        self.process()
        
    def process(self):
        self.min = [None, ] * 3
        self.max = [None, ] * 3
        for o in self.objects:
            for i in range(3):
                if self.min[i] is None or o.min[i] < self.min[i]:
                    self.min[i] = o.min[i]
                if self.max[i] is None or o.max[i] > self.max[i]:
                    self.max[i] = o.max[i]

    def save_to_file(self, filename):
        open(filename, 'wb').write(pickle.dumps(self.objects, 2))

    def convert_to_stl(self):
        if not all([numpy, mesh]):
            raise RuntimeError("scene_to_stl: numpy or mesh are not available, this will not work")

        count_polys = sum([len(obj.get_polys()) for obj in self.objects])
        mesh_data = numpy.zeros(count_polys, dtype=mesh.Mesh.dtype)
        i = 0
        for obj in self.objects:
            points = obj.get_points()
            for p in obj.get_polys():
                mesh_data['vectors'][i] = numpy.array([list(points[pi].pp()) for pi in p.indices])

                i += 1

        scene = mesh.Mesh(mesh_data)

        return scene

def make_cube(c, r):
    dx = Point(r, 0, 0)
    dy = Point(0, r, 0)
    dz = Point(0, 0, r)
    points = [
        c - dx - dy - dz,
        c - dx - dy + dz,

        c - dx + dy - dz,
        c - dx + dy + dz,

        c + dx - dy - dz,
        c + dx - dy + dz,

        c + dx + dy - dz,
        c + dx + dy + dz,
    ]

    points[0].n = (-1,-1,-1)
    points[1].n = (-1,-1,+1)
    points[2].n = (-1,+1,-1)
    points[3].n = (-1,+1,+1)

    points[4].n = (+1,-1,-1)
    points[5].n = (+1,-1,+1)
    points[6].n = (+1,+1,-1)
    points[7].n = (+1,+1,+1)

    polys = [
        [0, 1, 2],
        [2, 1, 3],

        [2, 0, 4],
        [2, 4, 6],

        [4, 0, 1],
        [4, 1, 5],

        [6, 4, 5],
        [6, 5, 7],

        [2, 6, 7],
        [2, 7, 3],

        [7, 5, 3],
        [3, 5, 1],
    ]
    polys = [Poly(p) for p in polys]

    cube = Object()
    cube.set_points(points)
    cube.set_polys(polys)

    return cube

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

