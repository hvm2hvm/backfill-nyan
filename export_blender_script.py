import sys
sys.path.append('/home/hvm/work/250_spaceapps/backfill-nyan')
from libobj import *
import bpy

objs = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name != '_root']
for o in objs:
    vertices = [v for v in o.data.vertices]
    myobj = Object()
    points = []
    for v in vertices:
        co = o.matrix_world * v.co
        n = [cc for cc in v.normal]
        points.append(Point(co.x, co.y, co.z, n))
    myobj.set_points(points)
    polys = []
    for p in o.data.polygons:
        indices = [i for i in p.vertices]
        if len(indices) == 3:
            polys.append(Poly(indices))
        elif len(indices) == 4:
            polys.append(Poly(indices[:2] + indices[3:]))
            polys.append(Poly(indices[3:] + indices[1:3]))
    myobj.set_polys(polys)
    myobj.save_to_file("%s.obj.pickle" % (o.name))
    
    
