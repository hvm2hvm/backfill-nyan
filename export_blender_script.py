import os
import sys
sys.path.append('../backfill-nyan')
from libobj import *
import bpy

c_filename = os.path.basename(bpy.data.filepath)
if c_filename.endswith('.blend'):
    c_filename = c_filename[:-6]

objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name != '_root']
nyan_objects = []
for o in objs:
    vertices = [v for v in o.data.vertices]
    nyan_obj = Object()
    points = []
    for v in vertices:
        co = o.matrix_world * v.co
        n = [cc for cc in v.normal]
        points.append(Point(co.x, co.y, co.z, n))
    nyan_obj.set_points(points)
    polys = []
    for p in o.data.polygons:
        indices = [i for i in p.vertices]
        if len(indices) == 3:
            polys.append(Poly(indices))
        elif len(indices) == 4:
            polys.append(Poly(indices[:2] + indices[3:]))
            polys.append(Poly(indices[3:] + indices[1:3]))
    nyan_obj.set_polys(polys)

    nyan_objects.append(nyan_obj)

scene = Scene(nyan_objects)
scene.save_to_file("%s.nyan" % (c_filename.lower()))
