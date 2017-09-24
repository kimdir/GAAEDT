""" Defines the evaluation functions for determining fitness values of 
	each member's design. A zero fitness score is default and marks a
	member as unfit for reproduction."""
import math
import utility_functions as utility
from pprint import pprint

design_factor = 1.75
	
def stress_eval(component, design_factor):
	""" Increments fitness score based on a design component's max 
		predicted stress and material yield. If a member's factor of 
		safety is lower than the design factor, the member is deemed 
		unfit for reproduction. Returns void."""
	
	# >>> Configured for metric system currently <<<
	material_yield = component.Material.yield_strength * 10 ** 6
	stress_vals = []
	for name,val in component.stress.items():
		# Check max stress against material yield stress to determine FoS
		try:
			component.safety_factors[name] = int(material_yield) / math.fabs(val)
		except ZeroDivisionError:
			component.safety_factors[name] = 10000
		except ValueError:
			print("Value Error: ")
			input(material_yield)
		
		# Check validity of design
		for i,sf in component.safety_factors.items():
			if sf < design_factor or sf > 5*design_factor:
				component.is_valid = False
		
		# Increment fitness value based on FoS distance from design factor
		for i,sf in component.safety_factors.items():	
			factor_target = 1.10 * design_factor
			target_offset = factor_target-1

			scale_factor = 2
			if sf < 1:
				component.is_valid = False
				return
			elif sf < factor_target:
				fit_mod = -0.5*math.cos((sf-1)*math.pi/target_offset)+0.5
			else:
				fit_mod_2 = -scale_factor * (math.pow((sf-1-target_offset),2) + 1)
				if fit_mod_2 < 0:
					fit_mod_2 = 0
				fit_mod_3 = target_offset/(2*(sf-1))
				fit_mod = fit_mod_2 + fit_mod_3
			max_score = 100
			fitness = max_score * fit_mod
			component.fitness += fitness
			
	return
	
def deflection_eval(member):
	""" Calculates the deflection of members based on 
	material properties and stresses and compares 
	them against thresholds in an external file. 
	Deflections above threshold evaluate as a bad 
	design, and fitness is determined by percent 
	deflection for any sub-threshold deflections."""	
	
def mass_eval(component):
	""" Increments fitness score based on the total mass of a component.
		No unfit condition applied. Returns void. """
	
	# >>> Scaling is hard-coded; consider revising
	# >>> Needs tuning once total mass typical values are determined
	scale_factor = 100
	component.fitness = scale_factor * 1/component.total_mass
	
	return

def price_eval(component):
	"""Increments fitness score based on estimated price using estimated 
		price per pound multiplied by the weight of material. If no 
		estimated price is available, assign 20 to the fitness score. No 
		failure conditions applied. Returns void."""
	if component.material_properties.Price == 'N/A':
		component.fitness += 20
	est_cost = component.mass * component.material_properties.Price
	
	# Will need to tune this function
	component.fitness += 1/est_cost * 1000
	return

def fluid_volume_eval(component):
	""" Increments fitness score based on the total working fluid 
		volume. A lower volume is preferred. No unfit condition applied. 
		Returns void."""
		
	pass

def force_eval(component):
	""" Increments fitness score based on maximum force expressed. A 
		design fails if it does not at minimum match the client data for
		the organic analog's capacity, and fitness drops rapidly if 
		expressed force is greater than 1.5 times the organic analog.
		Returns void."""
		
	pass

def accel_eval(component):
	""" Increments fitness score based on maximum acceleration based on 
		design mass and dynamics. A design fails if it does not at 
		minimum match the client data for the organic analog's capacity,
		and fitness drops rapidly if max acceleration is greater than 
		2 times the organic analog.	Returns void."""
		
	pass

def max_power_eval(member):
	""" Increments fitness score based on maximum power draw from a 
		member design. Lower power draw yields higher fitness scores. No
		unfit condition applied. Returns void."""
		
	pass

def fitness_evaluation(pop_list):
	""" Evaluates each component of each member of the population against
	fitness criteria and assigns a total fitness score for each member."""
	
	total_fitness = 0
	for mem in pop_list:
		if mem.is_evaluated == True:
			#~ print(" >>>>>> Already Evaluated <<<<<<")
			continue
			
		for comp_name,comp in mem.component_dict.items():
			stress_eval(comp,design_factor)
			mem.total_fitness =+ comp.fitness
		is_valid_check(mem)
		total_fitness += mem.total_fitness
		mem.is_evaluated = True

	return total_fitness

def is_valid_check(member):
	"""Checks members to see if there are any invalid 
		components in their design. If so, sets the 
		member's is_valid to False."""
	
	comp_names = utility.param_list_assign(member)
	for name in comp_names:
		comp = getattr(member,name)
		if comp.is_valid == False:
			member.is_valid = False
			break
	
	return

# >>> End <<<
