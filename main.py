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

        if len(self.scene.objects) == 1:
            print "in output paint"
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

time1 = 0.0
time2 = 0.0
time3 = 0.0

def sphere_int_triangle(c, r, t):
    global time1, time2, time3
    # note: thanks to Christer Ericson ( http://realtimecollisiondetection.net/blog/?p=103 )

    start = time.time()
    A = t[0] - c
    B = t[1] - c
    C = t[2] - c
    rr = r * r
    V = (B - A) ** (C - A)
    d = A * V
    e = V * V
    sep1 = d * d > rr * e
    time1 += time.time() - start

    aa = A * A
    ab = A * B
    ac = A * C
    bb = B * B
    bc = B * C
    cc = C * C
    sep2 = rr < aa < ab and ac > aa
    sep3 = rr < bb < ab and bc > bb
    sep4 = rr < cc < ac and bc > cc
    time2 += time.time() - start

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
    time3 += time.time() - start

    separated = sep1 or sep2 or sep3 or sep4 or sep5 or sep6 or sep7

    return not separated

class MainWindow(gui.QWidget):

    def __init__(self, parent=None):
        gui.QWidget.__init__(self, parent)

        self.scene_input = Scene('acrimsat_05.nyan')
        self.gl_input = GLDisplay(self, self.scene_input)

        self.resolution = 0.1
        self.scene_output = Scene()
        self.gl_output = GLDisplay(self, self.scene_output)
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
        locs = set()
        rems = set()
        print "building all locs"
        for xi in frange(min[0], max[0], self.resolution):
            for yi in frange(min[1], max[1], self.resolution):
                for zi in frange(min[2], max[2], self.resolution):
                    locs.add((xi, yi, zi))

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
        solved = 0
        for l in locs:
            for p in polys[:25]:
                if sphere_int_triangle(Point(*l), self.resolution, p):
                    rems.add(l)
            solved += 1
            if solved % 10 == 0:
                print "solved %d in total \r" % (solved),

        print """
    times:
        %5.2f
        %5.2f
        %5.2f
        """ % (time1, time2, time3)

        print "had %d entries, now have %d" % (len(locs), len(rems))

        print "building output objects"
        for l in rems:
            self.scene_output.add_object(make_cube(Point(*l), self.resolution / 2))

        # print "converting to stl and saving"

        # stl = self.scene_output.convert_to_stl()
        # stl.save('acrimsat_05.stl')


app = gui.QApplication(sys.argv)
w = MainWindow()
w.resize(1600, 900)
w.move(200, 50)
w.setWindowTitle('Default')
w.show()

sys.exit(app.exec_())
