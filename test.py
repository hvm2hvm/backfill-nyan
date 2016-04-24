import glob
import sys
import PyQt4 as qt
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui as gui
from PyQt4 import QtOpenGL as qgl

from libobj import *

class GLDisplay(qgl.QGLWidget):

    def __init__(self, parent):
        qgl.QGLWidget.__init__(self, parent)
        self.scene = Scene('themis.nyan')
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
        else:
            self.zoom /= 1.1
        self.repaint()

class MainWindow(gui.QWidget):

    def __init__(self, parent=None):
        gui.QWidget.__init__(self, parent)

        self.gl_display = GLDisplay(self)
        self.gl_display.move(0, 0)
        size = self.size()
        self.gl_display.resize(size.width(), size.height())

    def resizeEvent(self, e):
        size = self.size()
        self.gl_display.resize(size.width(), size.height())

app = gui.QApplication(sys.argv)
w = MainWindow()
w.resize(1600, 900)
w.move(200, 50)
w.setWindowTitle('Default')
w.show()

sys.exit(app.exec_())
