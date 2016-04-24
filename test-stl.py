import glob
from mpl_toolkits import mplot3d
from matplotlib import pyplot

from libobj import *

scene = Scene('tdrs.nyan').convert_to_stl()

figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(scene.vectors))

scale = scene.points.flatten(-1)
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()

scene.save('tdrs.stl')
