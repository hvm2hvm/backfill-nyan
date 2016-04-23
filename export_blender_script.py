import sys
sys.path.append('/home/hvm/work/250_spaceapps/backfill-nyan')
from libobj import *
import bpy

objs = [o for o in bpy.context.scene.objects]
print(objs)
