""" Defines the mutation fuctions for binary information crossover in a 
	genetic algorithm scheme. """
import utility_functions as utility
import genetic_algorithm_functions as gaf
import random

def transpose(binary_string, mutate_index, transpose_dir):
	""" Transposes the bit located at the mutate index up or down based 
	on input from the mutate evaluation. Returns the mutated binary 
	string."""
	
	#~ print(" >> (T) Transpose: " + str(transpose_dir))
	# Check transpose direction for valid value
	
	# Transpose the mutated binary bits
	transpose_index = (mutate_index + transpose_dir)
	if transpose_index == len(binary_string):
		transpose_index = 0
	bit_hold = binary_string[mutate_index]
	binary_string[mutate_index] = binary_string[transpose_index]

	binary_string[transpose_index] = bit_hold
	
	return binary_string
	
def invert(binary_string, index):
	""" Inverts a binary bit in the string located at the index. 
	Returns the modified binary string"""
	
	#~ print(" >> (I) Invert: " + str(binary_string[index]))
	if binary_string[index] == 0:
		binary_string[index] = 1
	else:
		binary_string[index] = 0
	return binary_string

def  mutate(binary_string, mutation_chance):
	""" Used after crossover and before decoding to determine if a bit 
	in the binary string mutates either via inversion or transposition. 
	Returns the modified binary string"""
	
	# Check if mutation occurs within this string and return to parent
	# function if no mutation occurs.
	
	i = 0
	while i < len(mutation_chance):
		if len(binary_string) == 0:
			input("Null Binary String")
		mutate_check = utility.chance_check(mutation_chance[i])
		if mutate_check == True:
			mutate_index = i
			mutation_chance[i] = utility.chance_modify(mutation_chance[i],mutate_check,"mutate")
		mutation_chance[i] = utility.chance_modify(mutation_chance[i],mutate_check,"mutate")
		i += 1
	if mutate_check == False:
		return binary_string
	
	# Determine type of mutation that occurs. Current options are 
	# inversion and transposition.
	mutate_selector = random.randint(1,99)
	if mutate_selector < 34:
		binary_string = transpose(binary_string, mutate_index, 1)
	elif mutate_selector < 67:
		binary_string = invert(binary_string, mutate_index)
	else:
		binary_string = transpose(binary_string, mutate_index, -1)
	return binary_string
	
