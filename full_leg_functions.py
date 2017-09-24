""" Describes the functions needed to evaluate the parameterized design
	as per the (supposed) drawings included in the folder. This file 
	changes based on the need of the client."""
import geometry, conversions, math, os
import utility_functions as utility
from utility_functions import name_get
import stress_calculations as sc
import genetic_algorithm_functions as gaf
import extfile_functions as extf
from __main__ import client_location
from full_leg_classes import *
from pprint import pprint

client_info = extf.import_client_info(client_location)


# >>> Configured for metric system and mm inputs <<<
LENGTH_CONVERT = 10**(-3)
AREA_CONVERT = 10**(-6)
VOL_CONVERT = 10**(-9)
MOI_CONVERT = 10**(-12)
PRESSURE_CONVERT = 6894.76

def cyl_stresses(cyl):
	""" Defines cylinder stresses. Stresses stored in the 
	cyl.stress class. Returns void."""
	
	cyl_pressure = int(cyl.force['cyl_pressure'])
	try:
		in_rad = cyl._inner_diameter/2 * LENGTH_CONVERT
		out_rad = in_rad+cyl.cyl_thickness * LENGTH_CONVERT
	except AttributeError:
		in_rad = cyl.inner_diameter/2 * LENGTH_CONVERT
		out_rad = in_rad + cyl.cyl_thickness * LENGTH_CONVERT
	try:
		cyl_stress = sc.pressure_vessel(in_rad,out_rad,cyl_pressure*PRESSURE_CONVERT)
	except ZeroDivisionError:
		cyl.is_valid = False
		return
	cyl.stress['tangential_stress'] = cyl_stress[0]
	cyl.stress['radial_stress'] = cyl_stress[1]
	cyl.stress['longitudinal_stress'] = cyl_stress[2]
	
	return

def cyl_mount_stresses(bone,prox_forces,dist_forces):
	""" Defines cylinder mount stresses. Stresses stored in the 
	bone.stress class. Returns void."""
	
	# Mount Stresses: 1D? Axial, 1D? Shear, 1D Bending
	hole_width = bone.mount_width/2 
	axial_area = geometry.area_rectangle(hole_width,bone.mount_thickness) * AREA_CONVERT
	shear_area = geometry.area_rectangle(bone.mount_width,bone.mount_thickness) * AREA_CONVERT
	
	# --> Axial & Shear:	
	try:	
		for index,val in prox_forces.items():
			bone.stress['prox_axial_stress'] = (sc.axial(val,axial_area))
			bone.stress['prox_shear_stress'] = (sc.axial(val,shear_area))
		for index,val in dist_forces.items():
			bone.stress['dist_axial_stress'] = (sc.axial(val,axial_area))
			bone.stress['dist_shear_stress'] = (sc.axial(val,shear_area))
	except ZeroDivisionError:
		bone.is_valid = False
		return
		
	# --> Bending:
	moi = geometry.moi_rectangle(bone.mount_thickness,bone.mount_width)
	lever = bone.mount_width
	for index,val in prox_forces.items():
		moment = val*lever
		bone.stress['prox_bending_stress' + index] = (sc.bending(moment,bone.mount_width/2,moi[0]))
	for index,val in dist_forces.items():
		moment = val*lever
		bone.stress['dist_bending_stress' + index] = (sc.bending(moment,bone.mount_width/2,moi[0]))		
	
	return

def structure_stresses(bone,prox_forces,dist_forces):
	""" Calculates the stresses for macro structural members. Stresses 
	stored in the bone.stress class. Returns void."""
	
	# Structure Stresses: 1D Axial, 2D Bending, 1D Torsion (Tibia only)
	
	# Find max cylinder forces for each end of the structure
	# >> Forces will be tensile
	max_prox_index, max_prox_force = utility.dict_search(prox_forces)
	max_dist_index, max_dist_force = utility.dict_search(dist_forces)
	
	# Calculate bending moment max lever
	bending_lever = (bone.core_diameter/2 + bone.mount_width)
	
	# Find max axial force
	max_axial = float(client_info['Weight']) - max_prox_force - max_dist_force

	# Calculate area and MoI for cross-section (x,y symmetric, rotated 45deg)
	rotate_deg = 45
	cs_area = (4 * geometry.rib_area(bone) + geometry.area_circle(bone.core_diameter/2,bone.core_inner_diameter/2)) * AREA_CONVERT
	
	# Calculate segment MoI
	try:
		length_to_segment = bone.core_diameter+bone.rib_length+bone.flange_thickness
		rib_seg_angle = geometry.segment_angle(length_to_segment,bone.flange_width/2)
		seg_moi_list = geometry.moi_segment(bone.calc_flange_radius,rib_seg_angle)
		seg_moi = 2 * seg_moi_list[0] + 2 * seg_moi_list[1]
	except ZeroDivisionError:
		bone.is_valid = False
		return
		
	# Calculate flange MoI
	f_moi1 = geometry.moi_rectangle(bone.flange_width,bone.flange_thickness,0,[length_to_segment-bone.flange_thickness/2,0])
	f_moi2 = geometry.moi_rectangle(bone.flange_thickness,bone.flange_width,0,[0,length_to_segment-bone.flange_thickness/2])
	flange_moi = 2 * f_moi1[0] + 2 * f_moi2[0]
	
	# Calculate rib MoI
	r_moi1 = geometry.moi_rectangle(bone.rib_width,bone.rib_length,0,[length_to_segment-bone.flange_thickness-bone.rib_length/2,0])
	r_moi2 = geometry.moi_rectangle(bone.rib_length,bone.rib_width,0,[0,length_to_segment-bone.flange_thickness-bone.rib_length/2])
	rib_moi = 2 * r_moi1[0] + 2 * r_moi2[0]	
	
	# Calculate cylinder MoI
	cyl_moi = geometry.moi_circle(bone.core_diameter/2,bone.core_inner_diameter/2)
	
	# Rotate the MoI by 45 degrees
	non_rotated_moi = [cyl_moi[0] + seg_moi + flange_moi + rib_moi, cyl_moi[1] + seg_moi + flange_moi + rib_moi]
	moi = geometry.moi_rotate(non_rotated_moi,rotate_deg)
	polar_moi = (moi[0] + moi[1]) * MOI_CONVERT
	
	# Separate forces into distinct coordinate components
	prox_x_forces = [n for x,n in prox_forces.items() if x.endswith('_fl') or x.endswith('_ex')]
	prox_y_forces = [n for x,n in prox_forces.items() if x.endswith('_ab') or x.endswith('_ad')]
	prox_z_forces = [n for x,n in prox_forces.items() if x.endswith('_ir') or x.endswith('_or')]
	dist_x_forces = [n for x,n in dist_forces.items() if x.endswith('_fl') or x.endswith('_ex')]
	dist_y_forces = [n for x,n in dist_forces.items() if x.endswith('_ab') or x.endswith('_ad')]
	dist_z_forces = [n for x,n in dist_forces.items() if x.endswith('_ir') or x.endswith('_or')]
	
	# --> Axial
	bone.stress['axial_stress'] = sc.axial(max_axial,cs_area)
	
	# --> Bending 
	# X-axis
	max_prox_x_index,max_prox_x_force = utility.dict_search(prox_x_forces)
	min_prox_x_index,min_prox_x_force = utility.dict_search(prox_x_forces,'min')
	max_dist_x_index,max_dist_x_force =utility.dict_search(dist_x_forces)
	min_dist_x_index,min_dist_x_force = utility.dict_search(dist_x_forces,'min')
	
	term1 = math.fabs(max_prox_x_force - max_dist_x_force)
	term2 = math.fabs(max_prox_x_force - min_dist_x_force)
	term3 = math.fabs(min_prox_x_force - min_dist_x_force)
	term4 = math.fabs(min_prox_x_force - max_dist_x_force)
	
	force_check_list = [term1,term2,term3,term4]
	max_bending_force = max(force_check_list)
	
	total_torque = max_bending_force * bending_lever
	
	# Record Stress
	try:
		bone.stress['bending_stress_x'] = sc.bending(total_torque,bone.calc_flange_radius,moi[0] * MOI_CONVERT)
	except ZeroDivisionError:
		bone.is_valid = False
		return
	
	# Y-axis
	max_prox_y_index,max_prox_y_force = utility.dict_search(prox_y_forces)
	min_prox_y_index,min_prox_y_force = utility.dict_search(prox_y_forces,'min')
	max_dist_y_index,max_dist_y_force = utility.dict_search(prox_y_forces)
	min_dist_y_index,min_dist_y_force = utility.dict_search(prox_y_forces,'min')
	
	try:
		term1 = math.fabs(int(max_prox_y_force) - int(max_dist_y_force))
		term2 = math.fabs(int(max_prox_y_force) - int(min_dist_y_force))
		term3 = math.fabs(int(min_prox_y_force) - int(min_dist_y_force))
		term4 = math.fabs(int(min_prox_y_force) - int(max_dist_y_force))
	except ValueError:
		pass	
	force_check_list = [term1,term2,term3,term4]
	max_bending_force = max(force_check_list)
	
	total_torque = max_bending_force * bending_lever
	
	# Record stress
	bone.stress['bending_stress_y'] = sc.bending(total_torque,bone.calc_flange_radius,moi[0] * MOI_CONVERT)
	
	# --> Torsion
	max_prox_z_index,max_prox_z_force = utility.dict_search(prox_z_forces,'max','rel')
	min_prox_z_index,min_prox_z_force = utility.dict_search(prox_z_forces,'min','rel')
	max_dist_z_index,max_dist_z_force = utility.dict_search(dist_z_forces,'max','rel')
	min_dist_z_index,min_dist_z_force = utility.dict_search(dist_z_forces,'min','rel')
	
	try:
		term1 = math.fabs(int(max_prox_z_force) - int(max_dist_z_force))
		term2 = math.fabs(int(max_prox_z_force) - int(min_dist_z_force))
		term3 = math.fabs(int(min_prox_z_force) - int(min_dist_z_force))
		term4 = math.fabs(int(min_prox_z_force) - int(max_dist_z_force))
	except ValueError:
		pass	
	force_check_list = [term1,term2,term3,term4]
	max_torsion_force = max(force_check_list)
	max_torque = max_torsion_force * bending_lever
	
	# Record stress
	bone.stress['torsion_stress'] = sc.torsion(max_torque,bone.calc_flange_radius,polar_moi * MOI_CONVERT)
	
	return

def gimbal_stresses(gimbal,joint_forces):
	""" Calculates the stresses on gimbal members. Stresses stored
	in the gimbal.stress class. Returns void."""
	
	# Gimbal Stresses:
	# Extended: 1D Axial (Mount), 2D Shear (Cross,Symmetric), 2D Bending (Cross)
	# Flexed (New Stresses): 1D Shear (Mount), 1D Bending (Mount) 
	# --> *Eval flexed at 90deg*
	
	# Separate forces into distinct coordinate components
	joint_x_forces = [n for x,n in joint_forces.items() if x.endswith('_fl') or x.endswith('_ex')]
	joint_y_forces = [n for x,n in joint_forces.items() if x.endswith('_ab') or x.endswith('_ad')]
	joint_z_forces = [n for x,n in joint_forces.items() if x.endswith('_ir') or x.endswith('_or')]
	
	body_force = float(client_info['Weight'])
	
	# 					>>>> Extended Stresses <<<<
	# --> 		Axial (Ignoring transverse axial load on pin)
	# > Z-axis >> mount
	axial_area = geometry.area_rectangle(gimbal.calc_mount_width,gimbal.mount_thickness) * AREA_CONVERT
	
	# Calculate max axial force (All pistons fully engaged)
	axial_force = body_force
	for n in joint_x_forces:
		axial_force += n
	for n in joint_y_forces:
		axial_force += n
	for n in joint_z_forces:
		axial_force += n	
	
	# Record stress
	try:
		gimbal.stress['ex_axial_stress'] = sc.axial(axial_force,axial_area)
	except ZeroDivisionError:
		gimbal.is_valid = False
		return
	# --> 		Shear >> pin
	# > X-axis (Y-axis is symmetric)
	
	shear_area = (math.pi/4 * gimbal.peg_diameter**2) * AREA_CONVERT
	# Calculate max force (All pistons fully engaged) and stress
	shear_force = axial_force	
	
	# Record stress
	gimbal.stress['ex_shear_stress'] = sc.axial(shear_force,shear_area)
	
	# --> 		Bending (Symmetric but inverted)
	# > X-axis
	bend_lever = (gimbal.peg_length - gimbal.peg_diameter)/2
	bend_force = axial_force
	bend_moment = bend_force * bend_lever
	
	moi = geometry.moi_circle(gimbal.peg_diameter/2) 
	
	# Record stress
	gimbal.stress['ex_bending_x'] = sc.bending(bend_moment,gimbal.peg_diameter/2,moi[0]* MOI_CONVERT)
	
	# > Y-axis
	gimbal.stress['ex_bending_y'] = -1 * gimbal.stress['ex_bending_x']
	
	# 					>>>> Flexed Stresses <<<<
	# --> Only calculating different stresses from extended position
	# --> 		Shear >> Mount
	
	shear_area = ((gimbal.peg_diameter - gimbal.calc_mount_width) * gimbal.mount_thickness) * AREA_CONVERT
	# Calculate max force (All pistons fully engaged) and stress
	shear_force = int(client_info['Weight'])
	try:
		gimbal.stress['fl_shear_stress'] = sc.axial(shear_force,shear_area)
	except ZeroDivisionError:
		gimbal.is_valid = False
		return
	
	# --> 		Bending >> Mount
	# > X-axis (Max at mount base)
	bend_lever = gimbal.calc_mount_height
	bend_force = int(client_info['Weight']) + math.sin(math.pi/4)*(axial_force-int(client_info['Weight']))
	bend_moment = bend_force * bend_lever
	
	
	moi = geometry.moi_rectangle(gimbal.mount_thickness,gimbal.calc_mount_width)
	gimbal.stress['fl_bending_x'] = sc.bending(bend_moment,gimbal.calc_mount_width/2,moi[0] * MOI_CONVERT)
	
	return
	
def piston_force(component):
	""" Defines the force output of the piston based on the max pressure
		of the actuator cylinder being analyzed. Returns maximum force 
		in pounds force."""
	
	# Convert mm to in
	r_head = conversions.mm_to_in(component.calc_r_head)
	
	# Calculate piston head area.
	head_area = geometry.area_circle(r_head) * AREA_CONVERT
	
	# Calculate force from area and pressure
	max_force = head_area * int(component.force['cyl_pressure']*PRESSURE_CONVERT)
	
	return max_force
	
def femur_interactions(member):
	""" Defines the force interactions between the hip actuators and 
	the thigh structure. Returns axial forces and offsets, transverse 
	forces and offsets, and bending and torsion moments."""
	
	#~ femur = name_get('FemurStructure',member)
	
	# Define acting forces
	force_hip = {}
	force_knee = {}
	force_hip['hip_ad'] = member.HipAdductCylinder.force['max_force']
	force_hip['hip_ab'] = member.HipAbductCylinder.force['max_force']
	force_hip['hip_ex'] = member.HipExtendCylinder.force['max_force']
	force_hip['hip_fl'] = member.HipFlexCylinder.force['max_force']
	
	force_knee['knee_ex'] = member.KneeExtendCylinder.force['max_force']
	force_knee['knee_fl'] = member.KneeFlexCylinder.force['max_force']
	
	structure_stresses(member.FemurStructure,force_hip,force_knee)
	cyl_mount_stresses(member.FemurStructure,force_hip,force_knee)
	
	return

def tibia_interactions(member):
	""" Defines the force interactions between the hip actuators and 
	the thigh structure. Returns axial forces and offsets, transverse 
	forces and offsets, and bending and torsion moments."""
	
	#~ tibia = name_get('TibiaStructure',member)
	
	# Define acting forces
	force_knee = {}
	force_ankle = {}
	force_ankle['ankle_ad'] = member.AnkleAdductCylinder.force['max_force']
	force_ankle['ankle_ab'] = member.AnkleAbductCylinder.force['max_force']
	force_ankle['ankle_ex'] = member.AnkleExtendCylinder.force['max_force']
	force_ankle['ankle_fl'] = member.AnkleFlexCylinder.force['max_force']
	force_ankle['ankle_ir'] = member.AnkleInternalCylinder.force['max_force']
	force_ankle['ankle_or'] = member.AnkleExternalCylinder.force['max_force']
	
	force_knee['knee_ex'] = member.KneeExtendCylinder.force['max_force']
	force_knee['knee_fl'] = member.KneeFlexCylinder.force['max_force']
	
	structure_stresses(member.TibiaStructure,force_knee,force_ankle)
	cyl_mount_stresses(member.TibiaStructure,force_knee,force_ankle)
	
	return

def foot_interactions(member):
	""" Defines the force interactions between the hip actuators and 
	the thigh structure. Returns axial forces and offsets, transverse 
	forces and offsets, and bending and torsion moments."""	
	
	pass

def hip_joint(member):
	""" Defines forces on the hip gimbal. Retunrs axial forces and 
	offsets, transverse forces and offsets, and bending and torsion 
	moments."""
	
	#~ hip = name_get('HipGimbal',member)
	
	# Define acting forces
	force_hip = {}
	force_hip['hip_ad'] = member.HipAdductCylinder.force['max_force']
	force_hip['hip_ab'] = member.HipAbductCylinder.force['max_force']
	force_hip['hip_ex'] = member.HipExtendCylinder.force['max_force']
	force_hip['hip_fl'] = member.HipFlexCylinder.force['max_force']
	
	gimbal_stresses(member.HipGimbal,force_hip)
	
	return

def knee_joint(member):
	""" Defines forces on the hip gimbal. Retunrs axial forces and 
	offsets, transverse forces and offsets, and bending and torsion 
	moments."""
	
	#~ knee = name_get('KneeGimbal',member)
	
	# Define acting forces
	force_knee = {}
	
	force_knee['knee_ex'] = member.KneeExtendCylinder.force['max_force']
	force_knee['knee_fl'] = member.KneeFlexCylinder.force['max_force']
	
	gimbal_stresses(member.KneeGimbal,force_knee)

	return
	
def ankle_joint(member):
	""" Defines forces on the hip gimbal. Retunrs axial forces and 
	offsets, transverse forces and offsets, and bending and torsion 
	moments."""
	
	#~ ankle = name_get('AnkleGimbal',member)
	
	# Define acting forces
	force_ankle = {}
	force_ankle['ankle_ad'] = member.AnkleAdductCylinder.force['max_force']
	force_ankle['ankle_ab'] = member.AnkleAbductCylinder.force['max_force']
	force_ankle['ankle_ex'] = member.AnkleExtendCylinder.force['max_force']
	force_ankle['ankle_fl'] = member.AnkleFlexCylinder.force['max_force']
	force_ankle['ankle_ir'] = member.AnkleInternalCylinder.force['max_force']
	force_ankle['ankle_or'] = member.AnkleExternalCylinder.force['max_force']
	
	gimbal_stresses(member.AnkleGimbal,force_ankle)

	return

def define_components(member):
	""" Defines derived values as per required for the design. Derived
		values should begin with a '~' for the search function to find 
		them. All cases are specific to the design. Returns void."""
	
	#~ input(member)
	
	# Check if component is already defined
	if member.is_defined == True:
		#~ print(" >>>>>> Already Defined <<<<<<")
		return
	
	# Calculate force output of all cylinders
	for i,comp in member.component_dict.items():
		if not('Cylinder' in comp.name):
			continue
		comp.force['max_force'] = piston_force(comp)
	
	# Calculate mass, stresses, and cost for each component
	for i,comp in member.component_dict.items():
		
		# Define component stress class variables
		comp.stress= {}
		comp.safety_factors = {}	
		comp.fitness = 0

		# Check for component type
		
		# ~~> Structures <~~
		if 'Structure' in comp.name:
			# Calculate structure member mass
			try:
				rib_vol = 4 * geometry.rib_area(comp) * comp.structure_length
				core_vol = 2 * geometry.vol_cyl(comp.core_thickness,comp.core_diameter/2)
			except ZeroDivisionError:
				comp.is_valid = False
				continue
			comp_mass = comp.Material.density * (rib_vol + core_vol)
			
			# Calculate stresses on structure
			if 'Femur' in comp.name:
				femur_interactions(member)
			if 'Tibia' in comp.name:
				tibia_interactions(member)	

		# ~~> Cylinders <~~		
		elif 'Cylinder' in comp.name:
			# Calculate cylinder member mass
			try:
				out_vol = geometry.vol_cyl(comp.cyl_length,(comp.inner_diameter/2 + comp.cyl_thickness))
				in_vol = geometry.vol_cyl((comp.cyl_length-2*comp.base_thickness),(comp.inner_diameter/2))
			except AttributeError:
				out_vol = geometry.vol_cyl(comp.cyl_length,comp._outer_diameter/2)
				in_vol = geometry.vol_cyl((comp.cyl_length-2*comp.base_thickness),(comp._outer_diameter/2 - comp.cyl_thickness))
			comp_mass = comp.Material.density * (out_vol - in_vol)

			# Calculate stresses on cylinder
			cyl_stresses(comp)
			
		# ~~> Gimbals <~~	
		elif 'Gimbal' in comp.name:
			# Calculate cross member mass
			peg_vol = 2 * geometry.vol_cyl(comp.peg_length,comp.peg_diameter/2)
			core_vol = geometry.vol_cyl(comp.peg_diameter,comp.peg_diameter/2)
			cyl_intersect = geometry.vol_cyl_intersect(comp.peg_diameter/2)
			#~ os.system('cls')
			#~ input(comp)
			comp_mass = comp.Material.density * (peg_vol + core_vol - 2 * cyl_intersect)
				
			# Calculate stresses on gimbal
			if 'Hip' in comp.name:
				hip_joint(member)
			elif 'Knee' in comp.name:
				knee_joint(member)
			elif 'Ankle' in comp.name:
				ankle_joint(member)
			else:
				print(comp.name)
				input("~Check1~ Component Name not defined.")
		else:
			print(comp.name)
			input("Component type not defined.")	

		# Increment member total mass and total cost
		member.total_mass += comp_mass
		try:
			member.total_cost += comp_mass * comp.Material['cost']
		except TypeError:
			#~ print("Missing cost information for " + str(comp.material_properties['name']))
			member.total_cost += comp_mass * 50
	
	member.is_defined = True
	
	return

# >>> End <<<
