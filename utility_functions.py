""" Contains utility functions for the program to facilitate with 
	handling of data."""
import random,math
from pprint import pprint

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
		not (a.startswith('__') or a == 'material_properties' 
		or a == 'XoverChance'
		or a == 'MutateChance' or a == 'MatProperties' 
		or a == 'member_index' or a == 'fitness' or a == 'Material'
		or a == 'is_valid' or a == 'forces' or a == 'age' 
		or a == 'total_cost' or a == 'total_mass' or a == 'total_fitness' 
		or a == 'safety_factors')]
	return param_list

def chance_modify(chance_val, prob_decrease, chance_type):
	""" Modifies the chance values based if the chance_eval returns a 
	true or false and the type of chance being evaluated. False slightly
	increases the chance, whereas True halves the probability."""
	
	# Set modifiers for the different chance types. *_up is a 
	# division factor, *_down is an increment factor.
	xover_up = 10
	xover_down = 0.05
	mutate_up = 10
	mutate_down = 0.05
	
	# Determine which mod set to use for the probability adjustment.
	if chance_type == "xover":
		# Modifying crossover chances, check for True/False condition
		if prob_decrease == True:
			chance_val /= xover_up
			#~ print(chance_val)	
		elif prob_decrease == False:
			chance_val += xover_down
			#~ print(chance_val)
		else:
			input("Xover Probability Direction Error")
		pass
	elif chance_type == "mutate":
		if prob_decrease == True:
			chance_val /= mutate_up
			#~ print(chance_val)
		elif prob_decrease == False:
			chance_val += mutate_down
			#~ print(chance_val)
		else:
			input("Mutate Probability Direction Error")
		pass
	else:
		input("Chance Modifier Type Error")
	return chance_val

def name_get(target,member,val = ''):
	""" Returns the target object of a call to a component with an ID 
	number attached based on a target name and component. If a value is 
	specified, returns specific value instead of target object."""
	
	targ_name = str(target) + ' ' + str(member.member_index)
	targ_obj = getattr(member,targ_name)
	if val != '':
		targ_val = getattr(targ_obj,val)
		return targ_val
	return targ_obj

def dict_search(old_val_dict,mode1 = 'max',mode2 = 'abs'):
	""" Searches a dictionary for absolute maximum values (or minimum if
	second attribute == 'min'). Passing 'rel' as third parameter 
	searches with relation to -inf instead of zero.  Returns max/min 
	index and value."""
	m_index = ''
	m_val = ''
	val_dict = {}
	
	if type(old_val_dict) == list:
		for val in old_val_dict:
			val_dict[str(val)] = val
	elif type(old_val_dict) == dict:
		val_dict = old_val_dict
	for index,val in val_dict.items():
		if m_index == '' and m_val == '':
			m_index = index
			m_val = val
			continue
		if mode1 == 'max':
			if mode2 == 'abs':
				if math.fabs(val) > math.fabs(m_val):
					m_index = index
					m_val = val
			elif mode2 == 'rel':
				if (val) > (m_val):
					m_index = index
					m_val = val	
			else:
				input("Mode2 Error")			
		elif mode1 == 'min':
			if mode2 == 'abs':
				if math.fabs(val) < math.fabs(m_val):
					m_index = index
					m_val = val
			elif mode2 == 'rel':
				if (val) < (m_val):
					m_index = index
					m_val = val	
			else:
				input("Mode2 Error")
		else:
			input("Mode1 Error")
	
	return m_index, m_val

def set_mat_properties(mat_ID,mat_list):
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

# ~~~ Binary Operations ~~~

def is_valid_population(pop_list):
	"""Checks the population list to ensure a valid generation. If 2/3's of the population is valid, returns is_valid as true. """
	
	is_valid = True
	invalid_count = 0
	
	for mem in pop_list:
		if mem.total_fitness < 1:
			invalid_count += 1
	
	if invalid_count >= 0:
		is_valid = False
	
	return is_valid

def print_member_fitness(pop_list):
	""" Prints the total fitness for all population members."""
	
	for mem in pop_list:
		print("Member Fitness: " + str(mem.total_fitness))

def binary_encode (value):
	"""Encodes a numerical value into a binary string"""
	#Values currently limited to integers, will consider decimals later
	bin_place = 6	
	
	# Special Case:
	if value == 0:
		bin_string = [0] * bin_place
		return bin_string

	#Construct binary string
	# Hard-coded values: consider revising. Upper value limit of 63

	bit_max = bin_place
	bin_string =[0] * bin_place
	current_sum =  0
	while bin_place >= 1:
		bit_val = 2**(bin_place-1)
		try:	
			val_test = int(value) - (bit_val)
		except ValueError:
			print(value)
			print(type(value))
			input("Value Error")
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

def min_max_member_fitness(pop_list):
	fitness_list = []
	max_fitness = 0
	min_fitness = 0
	for mem in pop_list:
		fitness_list.append(mem.total_fitness)
	max_fitness = max(fitness_list)
	min_fitness = min(fitness_list)
	
	return max_fitness, min_fitness
		

# ~~~ End ~~~
