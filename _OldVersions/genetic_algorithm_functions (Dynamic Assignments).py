"""Contains the following functions used to run genetic algorithms:
	initial population generation, crossover, mutation, and population
	regeneration."""
import random, os
import utility_functions as utility
import extfile_functions as extf
import mutation_functions as mutate
from __main__ import *
from pprint import pprint

# ~~~~~/~~~~~ Initialization Functions ~~~~~\~~~~~
def generate_initial_population(location,mat_location,force_location,member_count):
	"""Generates the initial random-characteristc population for the
		GA"""
		
	population_list=[0]*member_count
	master_class_dict = extf.initialize_classes(location)
	material_list, mat_names, unit_list = extf.build_material_list(mat_location)
	i = 0
	while i < member_count:
		subclass_name = ("PopMember" + " " + str(i))
		pop_type = type(str(subclass_name),(),{})
		pop_mem = gen_pop_member(pop_type,i,master_class_dict,mat_names,material_list,force_location)
		population_list[i] = pop_mem
		i += 1

	return population_list

def gen_pop_member(pop_member,member_index,master_class_dict,mat_names,material_list,force_location):
	"""Generates a population member based on the imported class
		attribute list"""
	
	# Initialize member variables
	init_member_classes(pop_member,master_class_dict)
	pop_member.total_fitness = 0
	pop_member.is_valid = True
	pop_member.age = 0
	pop_member.total_mass = 0
	pop_member.total_cost = 0
	pop_member_classes = utility.param_list_assign(pop_member)
	
	
	for x in pop_member_classes:
		if x == 'member_index' or x == 'stress':
			continue
		attr = getattr(pop_member,str(x))
		class_attrs = utility.param_list_assign(attr)

		des_val_count = len(utility.param_list_assign(attr))
		
		# Initialize non-random component variables
		attr.forces = extf.import_forces(force_location,x.split()[0])
		attr.XoverChance = []
		attr.MutateChance = []
		xover_list = attr.XoverChance
		mutate_list = attr.MutateChance
		attr.stress = {}
		attr.safety_factors = {}
		attr.fitness = 0

		i = 0
		xover_add = [0] * (des_val_count * 6)
		mutate_add = [0] * (des_val_count * 6)
		
		# Initialize random variables
		while i < des_val_count:
			xover_add[i] = random.randint(0,25)/100
			mutate_add[i] = random.randint(0,25)/100
			i += 1
		for l_add in xover_add:
			xover_list.append(l_add)
		for l_add in mutate_add:
			mutate_list.append(l_add)
		for y in class_attrs:
			
			# >>> Hard-coded threshold values; consider revising. <<<
			# >>> Hard-coded bitlength. Consider revivisng. <<<

			rand_val = random.randint(1,10)
			setattr(attr,y,rand_val)

		mat_ID = random.randint(1,len(material_list))
		attr.material_properties = set_mat_properties(attr,mat_ID,material_list)
	return pop_member

def set_mat_properties(pop_member,mat_ID,mat_list):
	MatProperties = {}
	#~ setattr(pop_member,('MatProperties'),{})
	# Cycles through material list looking for a matching name value
	for entry in mat_list:
		if int(entry['id']) == mat_ID:
			for k,v in entry.items():
				if k == 'ID':
					continue
				MatProperties[k] = v
	
	if MatProperties == {}:
		print(mat_ID)
		input("Material ID Error")
	return MatProperties

def init_member_classes(target,master_class_list):
	"""Sets the individual classes for each design component in a
		population member"""
	target.member_index = str(target.__name__).split()[1]
	total_count = 0
	for k,v in master_class_list.items():
		if k == 'stress':
			continue
		comp_name = (str(k) + " " + str(target.member_index))
		comp_class = type(comp_name,(),{})
		comp_class.member_index = target.member_index
		setattr(target,comp_name,comp_class)
		total_count += extf.assign_class_attr(location,comp_class,k)

	return total_count

# ~~~~~/~~~~~ Evaluation Functions ~~~~~\~~~~~

# ~~~~~/~~~~~ Crossover Functions  ~~~~~\~~~~~

def binary_encode (value):
	"""Encodes a numerical value into a binary string"""
	#Values currently limited to integers, will consider decimals later

	#~ print(" >> Starting binary_encode")
	# Special Case:
	if value == 0:
		bin_string = [0]
		return bin_string

	#Construct binary string
	# Hard-coded values: consider revising. Upper value limit of 63
	bin_place = 6
	bit_max = bin_place
	bin_string =[0] * bin_place
	current_sum =  0
	while bin_place >= 1:
		bit_val = 2**(bin_place-1)
		val_test = int(value) - (bit_val)
		current_sum += bit_val

		if current_sum > int(value):
			current_sum -= bit_val
			bin_string[bit_max-bin_place] = 0
		elif val_test < 0:
			bin_string[bit_max-bin_place] = 0
		else:
			bin_string[bit_max-bin_place] = 1
		bin_place -= 1
	return bin_string

def binary_decode(bin_string):
	"""Converts a list-formatted string of binary into a numerical value"""
	#Not actually a string as input.

	#Add values up bit wise
	i = 0
	bin_val = 0
	while i < len(bin_string):
		bit_val = 2**(len(bin_string)-1-i)
		bin_val += bin_string[i]*(bit_val)
		i += 1
	return bin_val

def chrom_binary_encode(chrom1):
	"""Encodes all values of a chromosome into a binary string for
	binary xover/mutation"""

	chrom1_binary = []
	attr_list = utility.param_list_assign(chrom1)
	attr_list.remove('stress')
	bitkey = [0]
	binary_key={}
	for des_val in attr_list:

		#Encode each gene into binary, ignoring string genes
		#(I.e. material)
		bit_sum = 0
		bin_string = binary_encode(getattr(chrom1,des_val))
		for s in bin_string:
			chrom1_binary.append(s)
		bit_sum = len(bin_string)
		bitkey.append(bit_sum+bitkey[-1])

	return chrom1_binary, bitkey

def chrom_binary_decode(chrom1, chrom1_bin, bitkey):
	"""Decodes a binary string into full values for each chromosome"""

	attr_list = utility.param_list_assign(chrom1)
	attr_list.remove('stress')
	bit_start = 0
	i = 0

	#Set destination chromosome
	bin_param = {}
	param_list = utility.param_list_assign(chrom1)
	param_list.remove('stress')

	#Separate binary chromosome string into binary genes
	for des_val in param_list:
		bit_end = int(bitkey[i+1])
		bin_param[des_val] = chrom1_bin[bit_start : bit_end]
		if (bit_end - bit_start) > 6:
			input("Bit Length Error")
		bit_start = bit_end
		i += 1

	#Decode binary genes into full value genes
	for k,v in bin_param.items():
		setattr(chrom1,k,binary_decode(v))
	return

def xover(chrom1_xover):
	xover_index = 1
	i = 1
	xover_check = False
	for item in chrom1_xover:
		if utility.chance_check(item):
			xover_index = i
			#~ print("Crossover at: " + str(xover_index))
			xover_check = True
			item = utility.chance_modify(item,xover_check,"xover")
			break
		item = utility.chance_modify(item,xover_check,"xover")
		i += 1
	return xover_index, xover_check

def chrom_xover_bin(chrom1, chrom2, chrom1_xover):
	"""Takes the binary string of two design components and performs
		crossover, returning the crossed binary strings. Crossover
		chance determined by the first design component."""
	#Binary crossover, so uses 0/1 instead of full values
	#Parameters delivered as lists of binary values

	# Determine xover point using the first design component's crossover
	# chance.
	xover_check = False
	while xover_check == False:
		xover_index, xover_check = xover(chrom1_xover)
		
		#~ if xover_check == False:
			#~ print("No crossover. Repeating...")

	#Perform xover

	xover_temp = chrom1[xover_index:]
	chrom1[xover_index:] = chrom2[xover_index:]
	chrom2[xover_index:] = xover_temp

	return chrom1, chrom2

def member_xover(member1, member2):
	""" Takes full population member profiles and performs crossover for
		each design component within it."""
	from _test import location, mat_location, force_location
	#~ print(">> Starting Member Xover...\n")

	# Compile the list of design components
	attr_list = utility.param_list_assign(member1)
	
	# Generate new parent members
	global next_mem	
	master_class_dict = extf.initialize_classes(location)
	material_list, mat_names, unit_list = extf.build_material_list(mat_location)
	subclass_name = ("PopMember" + " " + str(next_mem))

	
	pop_type = type(str(subclass_name),(),{})
	new_mem1 = gen_pop_member(pop_type,next_mem,master_class_dict,mat_names,material_list,force_location)
	next_mem += 1
	subclass_name = ("PopMember" + " " + str(next_mem))
	pop_type = type(str(subclass_name),(),{})
	new_mem2 = gen_pop_member(pop_type,next_mem,master_class_dict,mat_names,material_list,force_location)
	next_mem += 1
		
	# For each design component:
	for x in attr_list:

		# Define the general and member-specific name of the component,
		# and assign an object variable to the class
		attr = utility.define_target(x)
		attr1 = (attr + " " + str(member1.member_index))
		attr2 = (attr + " " + str(member2.member_index))
		new_attr1 = (attr + " " + str(new_mem1.member_index))
		new_attr2 = (attr + " " + str(new_mem2.member_index))
		member1_focus = getattr(member1,attr1)
		member2_focus = getattr(member2,attr2)
		new_member1_focus = getattr(new_mem1,new_attr1)
		new_member2_focus = getattr(new_mem2,new_attr2)
		print(new_member1_focus)

		# Convert the design component values into single binary string
		attr1_bin,bitkey1 = chrom_binary_encode(member1_focus)
		attr2_bin,bitkey2 = chrom_binary_encode(member2_focus)

		# Perform crossover between the two components
		# >> Passes a design component binary string into the function
		attr1_bin, attr2_bin = chrom_xover_bin(attr1_bin, attr2_bin,getattr(member1,attr1).XoverChance)

		# Checks for and performs mutation if it occurs

		attr1_bin = mutate.mutate(attr1_bin,member1_focus.MutateChance)
		attr2_bin = mutate.mutate(attr2_bin,member2_focus.MutateChance)
		
		# Convert binary string into design component values
		chrom_binary_decode(new_member1_focus,attr1_bin,bitkey1)
		chrom_binary_decode(new_member2_focus,attr2_bin,bitkey2)


	#~ print("Ending Member Xover...")
	return new_mem1, new_mem2

# ~~~ End ~~~
