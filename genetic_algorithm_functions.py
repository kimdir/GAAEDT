"""Contains the following functions used to run genetic algorithms:
	initial population generation, crossover, mutation, and population
	regeneration."""
import random, os

import utility_functions as utility
import extfile_functions as extf
import mutation_functions as mutate
import full_leg_functions as flf

from full_leg_classes import *
from __main__ import *
from pprint import pprint

# ~~~~~/~~~~~ Initialization Functions ~~~~~\~~~~~
def generate_initial_population(member_count):
	"""Generates the initial random-characteristc population for the
		GA"""
		
	population_list=[]

	while PopMember.next_mem < member_count:
		population_list.append(PopMember())
		os.system('cls')
		print("Population Count: " + str(len(population_list)))
		setattr(PopMember,'next_mem',PopMember.next_mem+1)
	
	return population_list
	
# ~~~~~/~~~~~ Crossover Functions  ~~~~~\~~~~~

def xover_point(chrom1_xover):
	""" Determines the crossover point based on the XoverChance variable from a selected population member"""
	
	xover_index = 1
	i = 1
	xover_check = False
	while xover_check == False:
		for item in chrom1_xover:
			if utility.chance_check(item):
				xover_index = i
				#~ print("Crossover at: " + str(xover_index))
				xover_check = True
				item = utility.chance_modify(item,xover_check,"xover")
				break
			chance_up = utility.chance_modify(item,xover_check,"xover")
			try:
				chrom1_xover[i] = chance_up
			except IndexError:
				print("XoverChance: ")
				print(chrom1_xover)
				print("Index at: " + str(i))
				print("List length: " + str(len(chrom1_xover)))
				input("Index Error")
			
			i += 1
		if i == (len(chrom1_xover)-1):
			i = 1
		
	return xover_index

def member_xover(member1, member2):
	""" Takes full population member profiles and performs crossover for
		each design component within it."""
	new_genome_dict1 = {}
	new_genome_dict2 = {}
	
	# Crossover each component's genome and store the new genome in a dictionary
	for comp_name,comp in member1.component_dict.items():
		# Assign component genome to a variable
		comp1 = comp
		comp2 = member2.component_dict[comp_name]
		
		try:
			genome1, key1 = comp1.binary_encode()
			genome2, key2 = comp2.binary_encode()
		except TypeError:
			print(comp1)
			print(comp2)
			input("Component Genome Assignment Error")
		
		# Pick a member to pull XoverChance from and find the crossover index.
		xover_index_list = [0] * random.randint(1,6)
		for list_val in xover_index_list:
			rand_val = random.randint(1,2)
			if rand_val == 1:
				list_val = (xover_point(comp1.XoverChance))
			else:
				list_val = (xover_point(comp2.XoverChance))
		
		# Perform crossover at indicated index
		for xover_index in xover_index_list:
			xover_temp = genome1[xover_index:]
			genome1[xover_index:] = genome2[xover_index:]
			genome2[xover_index:] = xover_temp
		
		# Check for equal length
		if not(len(genome1) == len(genome2)):
			print("\nComponent 1: " + comp1.name)
			print("Component 2: " + comp2.name)
			print("\n~~~~~~~~~~~~")
			print("\n>> Component 1 Variables:\n")
			pprint(comp1.variable_dict)
			print("\n>> Component 2 Variables:\n")
			pprint(comp2.variable_dict)
			print("\n~~~~~~~~~~~~")			
			print("\nGenome 1 Length: " + str(len(genome1)))
			print("Genome 2 Length: " + str(len(genome2)))
			input("Genome Crossover Length Error")
		
		# Check for mutation
		genome1 = mutate.mutate(genome1,comp1.MutateChance)
		genome2 = mutate.mutate(genome2,comp2.MutateChance)
		
		# Build list structure for genome information
		genome_info1 = [genome1,key1]
		genome_info2 = [genome2,key2]
			
		# Write new genomes to genome dictionaries
		new_genome_dict1[comp_name] = genome_info1
		new_genome_dict2[comp_name] = genome_info2
	
	# Initialize new population members
	new_mem1 = PopMember()
	new_mem2 = PopMember()
	
	# Write new genome information to the new population members
	new_mem1.assign_genome(new_genome_dict1)
	new_mem2.assign_genome(new_genome_dict2)
	
	# Assign material values to each component
	for comp_name,comp in member1.component_dict.items():
		new_mem1.component_dict[comp_name].Material = comp.Material
	for comp_name,comp in member2.component_dict.items():
		new_mem2.component_dict[comp_name].Material = comp.Material
	
	#~ input(type(new_mem1.Material))

	# Define new member evaluation standards
	flf.define_components(new_mem1)
	flf.define_components(new_mem2)
	
	return new_mem1, new_mem2

# ~~~ End ~~~
