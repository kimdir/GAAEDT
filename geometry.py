""" Defines functions for determining geometric characteristics of solid
	sections"""

import math, conversions

# ~~~ Area Functions ~~~

def area_circle(radius,in_radius=0):
	"""Calculates the area of a circle using the radius of the circle.
		If a second radius is provided, calculates area for a hollow
		circle. Returns area in unit^2."""
	
	area1 = math.pi*math.pow(radius,2)
	area2 = math.pi*math.pow(in_radius,2)
	area = area1 - area2
	
	return area

def area_rectangle(length, width):
	""" Calculates the area of a rectangle. Returns area in unit^2."""

	area = length * width
	return area
	
def area_triange(base, height):
	""" Calculates the area of a triangle. Returns area in unit^2."""
	
	area = 1/2 * base * height
	return area

def segment_angle(adjacent,opposite):
	""" Calculates the segment angle for the area_circ_segment function
		using the adjacent and opposite side lengths. Returns angle in 
		degrees. """
	
	seg_angle = conversions.rad_to_deg(2*math.atan(opposite/(adjacent)))
	
	return seg_angle
	
def area_circ_segment(seg_angle, radius):
	""" Calculates the area of a circular segment from sector area and 
	segment width. Angle should be passed in as degrees. 
	Returns area in units^2."""
	
	#Convert to radians
	rad_angle = math.pi/180 * seg_angle

	#Define segment area
	area_segment = radius*radius/2*(rad_angle - math.sin(rad_angle))
	
	return area_segment

def rib_area(component):
	""" Defines the area of a structural rib. Returns area in unit^2."""
	
	# Define component areas
	angle_length = (component.flange_width + component.rib_length + component.core_diameter)
	seg_angle = segment_angle(angle_length,(component.flange_width/2))
	area1 = area_circ_segment(seg_angle,component.calc_flange_radius)
	area2 = area_rectangle(component.flange_width,component.flange_thickness)
	area3 = area_rectangle(component.rib_width,component.rib_length)
	
	total_area = area1 + area2 + area3
	return total_area

# ~~~ Volume Functions ~~~

def vol_cyl(length, radius, in_radius = 0):
	""" Calculates the volume of a cylinder. If a third value is 
	supplied, calculates volume of a hollow cylinder. Returns volume in 
	unit^3."""
	
	volume = length * (area_circle(radius)-area_circle(in_radius))
	
	return volume

def vol_rect_prism(height, length, width):
	""" Calculates the volume of a rectangular prism. Returns volume in 
	unit^3."""
	
	volume = height * length * width
	
	return volume

def vol_fillet(radius, length):
	""" Calculates the volume of a fillet of constant radius over a 
	length. Returns volume in unit^3."""
	
	# Calculate prism volume
	prism_volume = vol_rect_prism(length, radius, radius)
	
	# Calculate cylinder quadrant volume
	cyl_volume = vol_cyl(length, radius)/4
	
	# Subtract cylinder quadrant from prism
	fillet_volume = prism_volume - cyl_volume
	
	return fillet_volume

def vol_cyl_intersect(radius):
	""" Defines the volume of the intersection of three perpendicular 
		cylinders of equal radius. Returns volume in unit^3."""
	
	coeff = 8 * (2 - math.sqrt(2))
	intersect_vol = coeff * radius ** 3
	
	return intersect_vol

# ~~~ Centroid/MoI Calculations ~~~

def moi_circle(radius, in_radius = 0, center_offset = [0,0]):
	""" Calculates the centroid and moment of inertia of a 2D circle 
		centered on the origin. If a second radius is provided, 
		calculates for a hollow circle. Offset should be coordinates in 
		the form [x,y] from axes of rotation. Assumes no offset unless 
		provided. Returns list moments of inertia for each axis, 
		accounting for offsets and parallel axis theorem. Output is: 
		[I_x, I_y, J_z]"""
		
	inertia_list = [0,0,0]
	
	# Calculate the moment of inertia of the shape
	inertia_list[0] = math.pi/4*(math.pow(radius,4)-math.pow(in_radius,4))
	inertia_list[1] = inertia_list[0]
	
	# If there is an offset, apply parallel axis theorem
	area = area_circle(radius, in_radius)
	inertia_list[0] += area*math.pow(center_offset[0],2)
	inertia_list[1] += area*math.pow(center_offset[1],2)
	
	# Calculate polar inertia
	inertia_list[2] = inertia_list[0] + inertia_list[1]			
	
	return inertia_list

def moi_rectangle(base, height, angle_offset = 0, center_offset = [0,0]):
	""" Calculates the centroid and moment of inertia of a 2D rectangle 
		centered on the origin. Offset should be coordinates in 
		the form [x,y]. Assumes no offet unless provided. Returns list 
		of moments of inertia foreach axis, accounting for offsets and 
		parallel axis theorem. Accepts an angle offset in degrees and 
		calculates for the rotation. Output is: [I_x, I_y, J_z]"""
		
	inertia_list = [0,0,0]
	
	# Convert angle offset to radians
	rad_offset = angle_offset * math.pi/180
	
	# Calculate the moment of inertia of the shape
	# > Base associated with x-axis
	coeff = base*height/12
	term1x = height**2 * math.pow(math.cos(rad_offset),2)
	term2x = base**2 * math.pow(math.sin(rad_offset),2)
	term1y = base**2 * math.pow(math.cos(rad_offset),2)
	term2y = height**2 * math.pow(math.sin(rad_offset),2)
	inertia_list[0] = coeff*(term1x + term2x)
	inertia_list[1] = coeff*(term1y + term2y)
	
	# If there is an offset, apply parallel axis theorem
	area = area_rectangle(base, height)
	inertia_list[0] += area*math.pow(center_offset[0],2)
	inertia_list[1] += area*math.pow(center_offset[1],2)
	
	# Calculate polar inertia
	inertia_list[2] = inertia_list[0] + inertia_list[1]			
	
	return inertia_list
		
def moi_segment(radius, segment_angle, angle_offset = 0):
	""" Calculates the centroid and moment of inertia of a 2D circular 
		segment whose parent circle is centered on the origin. Alignment
		determines which coordinate is aligned with the origin. Offset 
		should be coordinates in the form [x,y]. Assumes no offet unless
		provided. Returns list of moments of inertia for each axis. 
		Assumes a zero inclination, indicating a segment spanning 
		quadrants I and IV of a grid centered at the center of the 
		circle. Output is: [I_x, I_y, J_z]"""
		
	# Assumes symmetrical, therefor I_xy = 0	
	
	inertia_list = [0,0,0]
	centroid_list = [0,0]
	
	# Convert angle to radians
	segment_rads = math.pi/180 * segment_angle
	rads_offset = math.pi/180 * angle_offset
	
	# Calculate the moment of inertia of the shape
	inertia_list[0] = math.pow(radius,4)/8 * (segment_rads - math.sin(segment_rads) + 2*math.sin(segment_rads)*math.pow(math.sin(segment_rads/2),2))
	inertia_list[1] = math.pow(radius,4)/24 * (3*segment_rads - 3*math.sin(segment_rads) + 2*math.sin(segment_rads)*math.pow(math.sin(segment_rads/2),2))

	# Error check
	if inertia_list[0] < 0 or inertia_list[1] < 0:
		input("Inertia Sign Error")	
	
	# Calculate polar inertia
	inertia_list[2] = inertia_list[0] + inertia_list[1]			
			
	return inertia_list

def moi_rotate(inertias,theta):
	""" Calculates moment of inertia rotated around the centroid of an
		area based on rotation angle theta(in degrees). Returns modified
		MoI's as [Ix, Iy, Jz]. Assumes a symmetric cross-section. 
		(Ixy = 0)"""
	
	initial_x = inertias[0]
	initial_y = inertias[1]
	rad_offset = conversions.deg_to_rad(theta)
	inertia_list =[0,0,0]
	
	# Apply angle offset
	term1 = (initial_x + initial_y)/2
	term2 = (initial_x - initial_y)/2 * math.cos(2*rad_offset)
	inertia_list[0] = term1 + term2
	inertia_list[1] = term1 - term2	
	inertia_list[2] = inertia_list[0] + inertia_list[1]
	
	return inertia_list

# ~~~ 3D Moment of Inertia Calculations ~~~

# >>> End <<<
