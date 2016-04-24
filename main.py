import glob
import sys
import time
import PyQt4 as qt
from OpenGL.GL import *
import random
from OpenGL.GLU import *
from PyQt4 import QtGui as gui
from PyQt4 import QtOpenGL as qgl

from libobj import *

def frange(min, max, step):
    i = min
    if min <= max and step > 0 or min >= max and step < 0:
        while i <= max:
            yield i
            i += step

class GLDisplay(qgl.QGLWidget):

    def __init__(self, parent, scene=None):
        qgl.QGLWidget.__init__(self, parent)
        if scene is not None:
            self.scene = scene
        else:
            self.scene = Scene()
        self.clicking = False
        self.rx = 30
        self.ry = 30
        self.zoom = 1

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0, 0, -10)
        # glScalef(5, 5, 5)
        glScalef(*[self.zoom] * 3)
        # glColor3f(1.0, 1.0, 1.0)

        glRotatef(self.rx, 0, 1, 0)
        glRotatef(self.ry, 1, 0, 0)

        for obj in self.scene.objects:
            obj.run_gl()

        glFlush()

    def initializeGL(self):
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)
        # glFrontFace(GL_CW)

        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.0, 0.0, ])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, ])
        glMaterialfv(GL_FRONT, GL_SHININESS, 50.0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.0, 0.0, 0.0, ])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [6.0, 6.0, 6.0, ])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, ])
        glLightfv(GL_LIGHT0, GL_POSITION, [10,10,10])

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        self.initView()

    def initView(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0,0, self.width(), self.height())
        gluPerspective(45.0, 1.33, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)

    def resizeEvent(self, e):
        self.initView()

    def mouseMoveEvent(self, e):
        if self.clicking:
            self.rx = self.irx + 180 * (e.x() - self.mx) / self.width()
            self.ry = self.iry + 180 * (e.y() - self.my) / self.height()
            self.repaint()

    def mousePressEvent(self, e):
        self.clicking = True
        self.mx, self.my = e.x(), e.y()
        self.irx, self.iry = self.rx, self.ry

    def mouseReleaseEvent(self, e):
        self.clicking = False

    def wheelEvent(self, e):
        if e.delta() > 0:
            self.zoom *= 1.1
        elif e.delta() < 0:
            self.zoom /= 1.1
        self.repaint()

def dist(v1, v2):
    return ((v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2 + (v1.y - v2.y) ** 2) ** 0.5

def sphere_int_triangle(c, r, t):
    # note: thanks to Christer Ericson ( http://realtimecollisiondetection.net/blog/?p=103 )

    A = t[0] - c
    B = t[1] - c
    C = t[2] - c
    rr = r * r
    V = (B - A) ** (C - A)
    d = A * V
    e = V * V
    sep1 = d * d > rr * e

    aa = A * A
    ab = A * B
    ac = A * C
    bb = B * B
    bc = B * C
    cc = C * C
    sep2 = rr < aa < ab and ac > aa
    sep3 = rr < bb < ab and bc > bb
    sep4 = rr < cc < ac and bc > cc

    AB = B - A
    BC = C - B
    CA = A - C 
    d1 = ab - aa
    d2 = bc - bb
    d3 = ac - cc 
    e1 = AB * AB 
    e2 = BC * BC 
    e3 = CA * CA 
    Q1 = A * e1 - AB * d1
    Q2 = B * e2 - BC * d2 
    Q3 = C * e3 - CA * d3 
    QC = C * e1 - Q1
    QA = A * e2 - Q2 
    QB = B * e3 - Q3
    sep5 = Q1 * Q1 > rr * e1 * e1 and Q1 * QC > 0
    sep6 = Q2 * Q2 > rr * e2 * e2 and Q2 * QA > 0
    sep7 = Q3 * Q3 > rr * e3 * e3 and Q3 * QB > 0

    separated = sep1 or sep2 or sep3 or sep4 or sep5 or sep6 or sep7

    return not separated

def sit_np(c, r, polys):

    for t in polys:
        A = t[0] - c
        B = t[1] - c
        C = t[2] - c
        rr = r * r
        V = numpy.cross(B - A, C - A)
        d = numpy.dot(A, V)
        e = numpy.dot(V, V)
        sep1 = d * d > rr * e
        if sep1:
            continue

        aa = numpy.dot(A, A)
        ab = numpy.dot(A, B)
        ac = numpy.dot(A, C)
        bb = numpy.dot(B, B)
        bc = numpy.dot(B, C)
        cc = numpy.dot(C, C)
        sep2 = rr < aa < ab and ac > aa
        sep3 = rr < bb < ab and bc > bb
        sep4 = rr < cc < ac and bc > cc
        if sep2 or sep3 or sep4:
            continue

        AB = B - A
        BC = C - B
        CA = A - C
        d1 = ab - aa
        d2 = bc - bb
        d3 = ac - cc
        e1 = numpy.dot(AB, AB)
        e2 = numpy.dot(BC, BC)
        e3 = numpy.dot(CA, CA)
        Q1 = A * e1 - AB * d1
        Q2 = B * e2 - BC * d2
        Q3 = C * e3 - CA * d3
        QC = C * e1 - Q1
        QA = A * e2 - Q2
        QB = B * e3 - Q3
        sep5 = numpy.dot(Q1, Q1) > rr * e1 * e1 and numpy.dot(Q1, QC) > 0
        sep6 = numpy.dot(Q2, Q2) > rr * e2 * e2 and numpy.dot(Q2, QA) > 0
        sep7 = numpy.dot(Q3, Q3) > rr * e3 * e3 and numpy.dot(Q3, QB) > 0

        # separated = sep1 or sep2 or sep3 or sep4 or sep5 or sep6 or sep7
        if sep5 or sep6 or sep7:
            continue

        return True

    return False


leaves_global = set()


class OctTree(object):

    def __init__(self, x1, y1, z1, x2, y2, z2, res):
        if abs(x2-x1) < res / 10.0 or abs(y2-y1) < res / 10.0 or abs(z2-z1) < res / 10.0:
            self.possible = False
        else:
            self.possible = True

        self.res = res
        self.x1 = int(x1 / res) * res
        self.y1 = int(y1 / res) * res
        self.z1 = int(z1 / res) * res
        self.x2 = int(x2 / res) * res
        self.y2 = int(y2 / res) * res
        self.z2 = int(z2 / res) * res
        
        self.xlen = int(self.x2 - self.x1) / res
        self.ylen = int(self.y2 - self.y1) / res
        self.zlen = int(self.z2 - self.z1) / res
        
        self.has_poly = False

        self.children = None
        

    def create_children(self):
        x1, y1, z1, x2, y2, z2 = self.x1, self.y1, self.z1, self.x2, self.y2, self.z2

        xm = self.x1 + self.xlen / 2 * self.res
        ym = self.y1 + self.ylen / 2 * self.res
        zm = self.z1 + self.zlen / 2 * self.res
        
        self.children = [
            child for child in [
                OctTree(x1, y1, z1, xm, ym, zm, self.res),
                OctTree(x1, y1, zm, xm, ym, z2, self.res),
                OctTree(x1, ym, z1, xm, y2, zm, self.res),
                OctTree(x1, ym, zm, xm, y2, z2, self.res),

                OctTree(xm, y1, z1, x2, ym, zm, self.res),
                OctTree(xm, y1, zm, x2, ym, z2, self.res),
                OctTree(xm, ym, z1, x2, y2, zm, self.res),
                OctTree(xm, ym, zm, x2, y2, z2, self.res),
            ] if child.possible
        ]

    def poly_contained(self, p):
        min = numpy.array([self.x1, self.y1, self.z1], dtype=numpy.float64)
        max = numpy.array([self.x2, self.y2, self.z2], dtype=numpy.float64)
        for v in p:
            if all(v > min) and all(max > v):
                return True

        return False

    def add_poly(self, p):
        if self.poly_contained(p):
            self.has_poly = True
            if self.xlen >= 2 or self.ylen >= 2 or self.zlen >= 2:
                if self.children is None:
                    self.create_children()
                for child in self.children:
                    child.add_poly(p)
            else:
                # print "poly is contained in leaf: ", self.xlen, self.ylen, self.zlen, self.x1, self.y1, self.z1
                pass
                leaves_global.add((self.x1, self.y1, self.z1, self.x2, self.y2, self.z2))

    def get_leaves(self):
        if not self.has_poly:
            return []

        res = []

        for child in self.children:
            if child.has_poly:
                if child.xlen <= 1 and child.ylen <= 1 and child.zlen <= 1:
                    res.append((
                        child.x1 + self.res / 2,
                        child.y1 + self.res / 2,
                        child.z1 + self.res / 2,
                    ))
                elif child.children is not None and len(child.children) > 0:
                    res += child.get_leaves()

        return res

class MainWindow(gui.QWidget):

    def __init__(self, parent=None):
        gui.QWidget.__init__(self, parent)

        self.scene_input = Scene('acrimsat_05.nyan')
        self.gl_input = GLDisplay(self, self.scene_input)

        self.resolution = 0.1
        self.scene_output = Scene()
        self.gl_output = GLDisplay(self, self.scene_output)
        if len(sys.argv) == 2:
            if sys.argv[1] == 'numpy':
                self.solve_output_numpy(self.scene_input.min, self.scene_input.max)
            elif sys.argv[1] == 'octree':
                self.solve_output_octree(self.scene_input.min, self.scene_input.max)
        else:
            self.solve_output(self.scene_input.min, self.scene_input.max)

        self.update_layout()

    def resizeEvent(self, e):
        self.update_layout()

    def update_layout(self):
        size = self.size()

        self.gl_input.move(10, 100)
        self.gl_input.resize(size.width() / 2 - 20, size.height() - 200)

        self.gl_output.move(size.width() / 2 + 10, 100)
        self.gl_output.resize(size.width() / 2 - 20, size.height() - 200)

    def solve_output(self, min, max):
        locs = []
        rems = []
        print "building all locs"
        for xi in frange(min[0], max[0], self.resolution):
            for yi in frange(min[1], max[1], self.resolution):
                for zi in frange(min[2], max[2], self.resolution):
                    locs.append((xi, yi, zi))

        print "getting all polys"
        polys = []
        for o in self.scene_input.objects:
            for p in o.get_polys():
                points = o.get_points()
                np = []
                for i in p.indices:
                    np.append(points[i])
                polys.append(np)

        print "processing %d locs with %d polys" % (len(locs), len(polys))
        start = time.time()
        solved = 0
        for l in locs:
            for p in polys[:100]:
                if sphere_int_triangle(Point(*l), self.resolution / 2, p):
                    rems.append(l)

            solved += 1
            if solved % 10 == 0:
                print "solved %d in total \r" % (solved),

        print
        print "process took %5.2fs" % (time.time() - start)
        print

        print "had %d entries, now have %d" % (len(locs), len(rems))

        print "building output objects"
        for l in rems:
            self.scene_output.add_object(make_cube(Point(*l), self.resolution / 2))

    def solve_output_numpy(self, min, max):
        locs = []
        rems = []
        print "building all locs"
        for xi in frange(min[0], max[0], self.resolution):
            for yi in frange(min[1], max[1], self.resolution):
                for zi in frange(min[2], max[2], self.resolution):
                    locs.append((xi, yi, zi))

        print "getting all polys"

        polys = []
        for o in self.scene_input.objects:
            points = o.get_points()
            for p in o.get_polys():
                np = []
                for i in p.indices:
                    np.append(points[i].pp())
                polys.append(np)
        polys = numpy.array(polys, dtype=numpy.float64)

        print "processing %d locs with %d polys" % (len(locs), len(polys))
        start = time.time()
        solved = 0
        for l in locs[:100]:
            if sit_np(numpy.array(l), self.resolution / 2, polys):
                rems.append(l)

            solved += 1
            print "solved %d in total \r" % (solved),

        print
        print "process took %5.2fs" % (time.time() - start)
        print

        print "had %d entries, now have %d" % (len(locs), len(rems))

        print "building output objects"
        for l in rems:
            self.scene_output.add_object(make_cube(Point(*l), self.resolution / 2))

    def solve_output_octree(self, min, max):
        min = [co - self.resolution * 2 for co in min]
        max = [co + self.resolution * 2 for co in max]
        print "creating octree with bounds: ", min, max
        tree = OctTree(min[0], min[1], min[2], max[0], max[1], max[2], self.resolution)

        polys = []
        for o in self.scene_input.objects:
            points = o.get_points()
            for p in o.get_polys():
                np = []
                for i in p.indices:
                    np.append(points[i].pp())
                polys.append(np)
        polys = numpy.array(polys, dtype=numpy.float64)

        print "adding %d polys" % (len(polys))
        for poly in polys:
            tree.add_poly(poly)

        print leaves_global

        leaves = tree.get_leaves()
        print "generated %d leaves" % (len(leaves))

        for l in leaves:
            self.scene_output.add_object(make_cube(Point(*l), self.resolution / 2))


app = gui.QApplication(sys.argv)
w = MainWindow()
w.resize(1600, 900)
w.move(200, 50)
w.setWindowTitle('Default')
w.show()

sys.exit(app.exec_())
