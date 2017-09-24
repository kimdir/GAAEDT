""" Defines the equations for mechanical stress and strain in three 
	dimensions."""
import math

# ~~~ Pure Stress Functions ~~~
	
def axial(force,area):
	""" Calculates axial/shear stress based on force and cross-sectional area.
	Returns stress in psi or Pa."""
	
	try:
		stress = force / area
	except ZeroDivisionError:
		stress = 999999999
	return stress
	
def bending(torque,max_dist,inertia_moment):
	""" Calculates the max bending stress based on torque/moment, 
	longest distance from midline, and moment of inertia. 
	Returns stress in psi or Pa."""
	
	try:
		stress = torque * max_dist / inertia_moment
	except ZeroDivisionError:
		stress = 999999999
	return stress
	
def torsion(torque, radius, polar_moment = 0, in_radius = 0):
	""" Calculates max torque for a circular cross section by default. 
	Calculates for a given polar moment if one is provided. If an inner 
	radius value is provided, calculates for a hollow cylinder. 
	Returns shear stress in psi or Pa."""
	
	if polar_moment == 0:
		# Calculate polar moment of inertia
		polar_moment = math.pi/32 * (math.pow(2*radius,4) - math.pow(2*in_radius,4))
	
	# Calculate stress
	try:	
		stress = torque * radius / polar_moment
	except ZeroDivisionError:
		stress = 999999999
	return stress

def buckling(length, area, moment_inertia, elastic_mod, yield_str, force):
	""" Calculates buckling stresses for axial members in compression.
		Uses the appropriate calculation based on the slenderness ratio.
		Assumes rounded-rounded end conditions. Assumes centric loading.
		Returns 'does_fail' boolean for buckling failure."""
		
	# Calculate slenderness ratio
	rad_gyr = math.sqrt(moment_inertia/area)
	slender_ratio = length/rad_gyr
	
	# Calculate slenderness threshold for long members
	slender_thresh = sqrt((2*math.pi*math.pi*elastic_mod)/yield_str)
	
	# Determine if long or intermediate member and calculate accordingly
	if slender_ratio > slender_thresh:
		# Long member calculation
		max_stress = math.pi*math.pi*elastic_mod/(math.pow(slender_ratio,2))
	elif slender_ratio <= slender_thresh:
		# Intermediate member calculation
		max_stress = yield_str - math.pow((yield_str/(2*math.pi))*slender_ratio,2)/elastic_mod
	else:
		input(">>>> Slenderness Ratio Error <<<<")
	
	# Check if member fails in buckling
	max_force = max_stress * area
	does_fail = False
	if max_force >= force:
		does_fail = True
	
	return does_fail

def contact(component1,component2, diam1, diam2, contact_length, load_force):
	""" Calculates contact stresses between two separate cylinders or 
		surfaces. Input	diameter of zero for a flat plane. One surface
		must be curved for this calculation to be performed. Negative 
		diameters indicate internal surfaces. Returns x,y,z stress for 
		member 1 and then member 2 in psi or Pa."""
	
	# Define radius of contact between surfaces
	term1 = 3*load_force/(math.pi*contact_length)
	term2 = (1-math.pow(component1.material_properties.poissons_ratio,2))/component1.material_properties.elastic_modulus
	term3 = (1-math.pow(component2.material_properties.poissons_ratio,2))/component2.material_properties.elastic_modulus
	if diam1 == 0:
		term4 = 0
	term4 = (1/diam1)
	if diam2 == 0:
		term5 = 0
	term5 = (1/diam2)
	
	term_cubed = term1 * (term2 +term3)/(term4 + term5)
	contact_radius = term_cubed **(1./3)
	
	# Calculate maximum pressure
	max_pressure = 2*load_force/(math.pi*contact_radius*contact_length)
	
	# Calculate max stresses
	stress_x1 = -2*max_pressure*component1.material_properties.poissons_ratio
	stress_x1 = -2*max_pressure*component1.material_properties.poissons_ratio
	
	stress_y1 = -1 * max_pressure
	stress_y2 = stress_y1
	
	stress_z1 = stress_y1
	stress_z2 = stress_y2
	
	stress1 = [stress_x1,stress_y1,stress_z1]
	stress2 = [stress_x2,stress_y2,stress_z2]
	
	return stress1, stress2

def pressure_vessel(in_rad, out_rad, in_pres, out_pres = 0):
	""" Calculates max pressure vessel stresses based on internal and 
		external pressure and internal and external radius. Assumes 
		external pressure is zero if no value is supplied. Returns list 
		of tangential, radial, and longetudinal stresses in that 
		order in psi or Pa."""
	
	# Calculate individual terms for shortened code
	term1 = in_pres * in_rad**2
	term2 = out_pres * out_rad**2
	term3 = out_rad**2 * (out_pres-in_pres)
	term4 = (out_rad**2 - in_rad**2)
	
	# Calculate tangential, radial, and longitudinal stress
	stresses =[0,0,0]
	stresses[0] = (term1 - term2 - term3)/term4
	stresses[1] = (term1 - term2 + term3)/term4
	stresses[2] = term1/term4		
	
	return stresses

# ~~~ Stress Evaluation Functions ~~~

def von_mises(sig_x, sig_y = 0, sig_z = 0, tau_x = 0, tau_y = 0, tau_z = 0):
	""" Calculates von Mises stresses for stress analysis. 
	Returns stress in psi or Pa."""
	
	# Define normal stress terms
	sterm1 = math.pow(sig_x-sig_y,2)
	sterm2 = math.pow(sig_y-sig_z,2)
	sterm3 = math.pow(sig_z-sig_x,2)
	
	# Define shear stress terms
	tterm1 = math.pow(tau_x,2)
	tterm2 = math.pow(tau_y,2)
	tterm3 = math.pow(tau_z,2)
	
	# Define equation coefficient
	coeff = 1/math.sqrt(2)
	
	# Calculate von Mises stress
	vm_stress = coeff * math.sqrt(sterm1 + sterm2 + sterm3 + 6*(tterm1 + tterm2 + tterm3))
	
	return vm_stress
	
# >>> End <<<
