import math
from libobj import *


def get_cone(r, h):
    points = [Point(0, 0, h, (0,0,1))]
    polys = []

    for i in range(32):
        a = 2 * math.pi * i / 32
        px = math.cos(a) * r
        py = math.sin(a) * r
        p = Point(px, py, 0)
        points.append(p)

    for i in range(32):
        if i<31:
            i1 = i+1
            i2 = i+2
        else:
            i1 = i+1
            i2 = 1

        n = triangle_normal(points[0], points[i1], points[i2])
        print n
        points[i1].n = n
        points[i2].n = n

        polys.append(Poly([0,i1,i2]))

    obj = Object()
    obj.set_points(points)
    obj.set_polys(polys)

    return obj
