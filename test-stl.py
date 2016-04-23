import glob
from mpl_toolkits import mplot3d
from matplotlib import pyplot

from libobj import *

objects = [
    Object(fn) for fn in glob.glob('*.obj.pickle')
]

scene = scene_to_stl(objects)


figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(scene.vectors))

scale = scene.points.flatten(-1)
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()

scene.save('scene.stl')
