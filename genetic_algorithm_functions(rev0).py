"""Contains the following functions used to run genetic algorithms:
	initial population generation, crossover, mutation, and population
	regeneration."""
import random, os
import extfile_functions as extf
import mutation_functions as mutate
from __main__ import location
from pprint import pprint

# ~~~~~/~~~~~ Initialization Functions ~~~~~\~~~~~
def generate_initial_population(location,mat_location,member_count):
	"""Generates the initial random-characteristc population for the
		GA"""

	population_list=[0]*member_count
	master_class_dict = extf.initialize_classes(location)
	material_list, mat_names = extf.build_material_list(mat_location)
	class PopMember(object):
		pass
	PopParent = PopMember()
	parent_list = (PopParent,)
	i = 0
	while i < member_count:
		subclass_name = ("PopMember" + " " + str(i))
		pop_type = type(str(subclass_name),(),{})
		pop_mem = gen_pop_member(pop_type,i,master_class_dict,mat_names,material_list)
		population_list[i] = pop_mem
		i += 1

	return population_list

def gen_pop_member(pop_member,member_index,master_class_dict,mat_names,material_list):
	"""Generates a population member based on the imported class
		attribute list"""

	init_member_classes(pop_member,master_class_dict)
	pop_member_classes = param_list_assign(pop_member)

	for x in pop_member_classes:
		if x == 'member_index':
			continue
		attr = getattr(pop_member,str(x))
		class_attrs = param_list_assign(attr)

		attr.XoverChance = []
		attr.MutateChance = []
		attr.Fitness = 0
		xover_list = attr.XoverChance
		mutate_list = attr.MutateChance

		i = 0

		xover_add = [0] * len(pop_member_classes)
		mutate_add = [0] * len(pop_member_classes)
		while i < len(pop_member_classes):
			xover_add[i] = random.randint(0,25)/100
			mutate_add[i] = random.randint(0,5)/100
			i += 1
		for l_add in xover_add:
			xover_list.append(l_add)
		for l_add in mutate_add:
			mutate_list.append(l_add)
		for y in class_attrs:
			# >>> Hard-coded threshold values; consider revising. <<<
			# >>> Hard-coded bitlength. Consider revivisng. <<<

			if y == 'Material':
				mat_chosen = random.choice(mat_names)
				attr = set_mat_properties(attr,mat_chosen,material_list)
				setattr(attr,y,random.choice(mat_names))
				continue
			rand_val = random.randint(1,10)
			setattr(attr,y,rand_val)
	return pop_member

def set_mat_properties(pop_member,mat_name,mat_list):

	setattr(pop_member,('MatProperties'),{})
	# Cycles through material list looking for a matching name value
	for entry in mat_list:
		if entry['Name'] == mat_name:
			for k,v in entry.items():
				if k == 'Name':
					continue
				pop_member.MatProperties[k] = v
	return pop_member

def init_member_classes(target,master_class_list):
	"""Sets the individual classes for each design component in a
		population member"""
	target.member_index = str(target.__name__).split()[1]
	for k,v in master_class_list.items():
		comp_name = (str(k) + " " + str(target.member_index))
		comp_class = type(comp_name,(),{})
		comp_class.member_index = target.member_index
		setattr(target,comp_name,comp_class)
		extf.assign_class_attr(location,comp_class,k)
	return

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
	attr_list = param_list_assign(chrom1)
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

	attr_list = param_list_assign(chrom1)
	bit_start = 0
	i = 0

	#Set destination chromosome
	bin_param = {}
	param_list = param_list_assign(chrom1)

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
		if chance_check(item):
			xover_index = i
			#~ print("Crossover at: " + str(xover_index))
			xover_check = True
			chance_modify(item,xover_check,"xover")
			break
		chance_modify(item,xover_check,"xover")
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

	#~ print(">> Starting Member Xover...\n")

	# Compile the list of design components
	attr_list = param_list_assign(member1)

	# For each design component:
	for x in attr_list:

		# Define the general and member-specific name of the component,
		# and assign an object variable to the class
		attr = define_target(x)
		attr1 = (attr + " " + str(member1.member_index))
		attr2 = (attr + " " + str(member2.member_index))
		member1_focus = getattr(member1,attr1)
		member2_focus = getattr(member2,attr2)

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
		chrom_binary_decode(member1_focus,attr1_bin,bitkey1)
		chrom_binary_decode(member2_focus,attr2_bin,bitkey2)


	#~ print("Ending Member Xover...")
	return

# ~~~~~/~~~~~ Mutation Functions  ~~~~~\~~~~~

# --> See mutation_functions.py <--

# ~/~ Utility Functions ~\~

def print_member(member):
	""" Prints the contents of a population member with some display
		options."""

	attr_list = param_list_assign(member)
	cls_toggle = False
	print_all = False
	for attr in attr_list:
		print('\n ~~~~~' + attr + '~~~~~\n')
		des_list = param_list_assign(getattr(member,attr))
		for des in des_list:
			print(des + ": " + str(getattr(getattr(member,attr),des)))
		if print_all == True:
			continue
		exit_flag = input("\nEnter 'y' to continue, 'cls' to clear the screen, or 'all' to print all members: ")
		if exit_flag == 'cls':
			cls_toggle = not(cls_toggle)
		elif exit_flag == 'all':
			print_all = True
		elif exit_flag != 'y':
			if cls_toggle == True:
				os.system('cls')
			break

def chance_check(threshold):
	""" Evaluates a probabliliy condition as True or False based on a
		provided threshold. Returns a boolean."""

	trigger = False
	chance_val = random.random()
	if chance_val < threshold:
		trigger = True
	return trigger

def define_target(target):
	general_name = str(target).split()[0]
	return general_name

def param_list_assign(target):
	""" Defines the contents of a class, ignoring non-GA variables and 
		class methods. """

	param_list = [a for a in  dir(target) if
		not (a.startswith('__') or a == 'Material' or a == 'XoverChance'
		or a == 'MutateChance' or a == 'MatProperties' 
		or a == 'member_index' or a == 'Fitness')]
	return param_list

def chance_modify(chance_val, prob_decrease, chance_type):
	""" Modifies the chance values based if the chance_eval returns a 
	true or false and the type of chance being evaluated. False slightly
	increases the chance, whereas True halves the probability."""
	
	# Set modifiers for the different chance types. *_up is a 
	# division factor, *_down is an increment factor.
	xover_up = 2
	xover_down = 0.05
	mutate_up = 2
	mutate_down = 0.005
	
	# Determine which mod set to use for the probability adjustment.
	if chance_type == "xover":
		# Modifying crossover chances, check for True/False condition
		if prob_decrease == True:
			chance_val += xover_down
		elif prob_decrease == False:
			chance_val /= xover_up
		else:
			input("Xover Probability Direction Error")
		pass
	elif chance_type == "mutate":
		if prob_decrease == True:
			chance_val += mutate_down
		elif prob_decrease == False:
			chance_val /= mutate_up
		else:
			input("Mutate Probability Direction Error")
		pass
	else:
		input("Chance Modifier Type Error")
	return(chance_val)
	
	
	
