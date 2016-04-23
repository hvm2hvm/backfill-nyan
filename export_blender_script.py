import sys
sys.path.append('/home/hvm/work/250_spaceapps/backfill-nyan')
from libobj import *
import bpy

objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in objs:
    vcoords = [v.co for v in o.data.vertices]
    print (o.name, ": ", len(vcoords), " vertices")
    myobj = Object()
    myobj.set_points([Point(v.x, v.y, v.z) for v in vcoords])
    myobj.set_polys([Poly([i for i in p.vertices]) for p in o.data.polygons])
    myobj.save_to_file("%s.obj.pickle" % (o.name))
    
    
