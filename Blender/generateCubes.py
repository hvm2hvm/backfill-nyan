import bpy
from collections import namedtuple
from bpy import context

create_cube = bpy.ops.mesh.primitive_cube_add

# dimensions are in mm ??
_3d_dimension = namedtuple("_3d_dimension", "x y z")
cube_length = 30

# the dimension of the entire space (eventually bounding box of 3d object)
space_size = _3d_dimension(x = 180, y = 120, z = 100)


for x_index in range (0, int(space_size.x / cube_length)):
	for y_index in range (0, int(space_size.y / cube_length)):
		for z_index in range (0, int(space_size.z / cube_length)):
			
			x_center = x_index * cube_length + cube_length / 2
			y_center = y_index * cube_length + cube_length / 2
			z_center = z_index * cube_length + cube_length / 2

			create_cube(location=(x_center, y_center, z_center), radius= (cube_length / 2) * 0.9)