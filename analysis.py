from libobj import *

obj = Object('foil_gold.obj.pickle')

# for p in obj.data['points']:
#     print p

points = obj.data['points']

for p in obj.data['polys']:
    print p
    for pi in p.indices:
        pp = points[pi]
        print '  ', pp
