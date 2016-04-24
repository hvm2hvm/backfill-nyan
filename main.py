import glob
import sys
import PyQt4 as qt
from OpenGL.GL import *
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

def sphere_int_triangle(c, r, t):
    # note: thanks to Christer Ericson ( http://realtimecollisiondetection.net/blog/?p=103 )

    A = t[0] - c
    B = t[1] - c
    C = t[2] - c
    V = (B-A).cross(C-A)
    d = A.dot(V)
    e = V.dot(V)
    separated = d * d > r * r * e

    if separated:
        return False

    aa = A.dot(A)
    ab = A.dot(B)
    ac = A.dot(C)
    bb = B.dot(B)
    bc = B.dot(C)
    cc = C.dot(C)
    rr = r * r
    separateda = (aa > rr) and (ab > aa) and (ac > aa)
    separatedb = (bb > rr) and (ab > bb) and (bc > bb)
    separatedc = (cc > rr) and (ac > cc) and (bc > cc)
    separated = separateda or separatedb or separatedc

    if separated:
        return False

    AB = B - A
    BC = C - B
    CA = A - C

    d1 = A.dot(AB)
    e1 = AB.dot(AB)
    d2 = B.dot(BC)
    e2 = BC.dot(BC)
    d3 = C.dot(CA)
    e3 = CA.dot(CA)

    Q1 = A * e1 - AB * d1
    QC = C * e1 - Q1
    Q2 = B * e2 - BC * d2
    QA = A * e1 - Q2
    Q3 = C * e3 - CA * d3
    QB = B * e3 - Q3

    separated1 = Q1.dot(Q1) > r * r * e1 * e1 and Q1.dot(QC) > 0
    separated2 = Q2.dot(Q2) > r * r * e2 * e2 and Q2.dot(QA) > 0
    separated3 = Q3.dot(Q3) > r * r * e3 * e3 and Q3.dot(QB) > 0
    separated = separated1 or separated2 or separated3

    if separated:
        return False

    return True

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
            for p in polys[:100]:
                if sphere_int_triangle(Point(*l), self.resolution, p):
                    rems.add(l)
            solved += 1
            print "solved %d in total \r" % (solved),

        print "had %d entries, now have %d" % (len(locs), len(rems))

        for l in rems:
            self.scene_output.add_object(make_cube(Point(*l), self.resolution / 2))

        stl = self.scene_output.convert_to_stl()
        stl.save('acrimsat_05.stl')
        

app = gui.QApplication(sys.argv)
w = MainWindow()
w.resize(1600, 900)
w.move(200, 50)
w.setWindowTitle('Default')
w.show()

sys.exit(app.exec_())
