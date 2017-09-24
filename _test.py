location = 'class_attributes.txt'
material_location ='material_properties.csv'
force_location ='component_forces.txt'
client_location ='client_info.csv'

import utility_functions as utility
import extfile_functions as extf
import genetic_algorithm_functions as gaf
import roulette_selection as roulette
import stress_calculations as stress
import fitness_evaluation as fe
import full_leg_functions as flf
import time
from full_leg_classes import *
import os, random, geometry, datetime
from pprint import pprint

member_count = 100
generation_count = 150
cycle_count = 10
current_cycle = 0

valid_gen = False

client_info = extf.import_client_info(client_location)
while current_cycle < cycle_count: 
	pop_count_list = []
	max_fitness_list = []
	total_fitness_list = []
	start = time.time()

	#~ random.seed(datetime.datetime.now)
	pop_list = []
	pop_list = gaf.generate_initial_population(member_count)
	setattr(PopMember,'is_initial_gen',False)

	for member in pop_list:
		flf.define_components(member)
	fe.fitness_evaluation(pop_list)
	reset_count = 0
				
	while valid_gen == False:
		valid_gen = utility.is_valid_population(pop_list)
		
		if reset_count > 200:
			i = 0
			while i < len(pop_list):
				if mem.total_fitness < 1:
					pop_list.pop(i)
				i += 1
			valid_gen = True
		elif valid_gen == False:
			good_mem = 0
			print("Bad generation, repeating...")
			setattr(PopMember,'is_initial_gen',True)
			setattr(PopMember,'next_mem',0)
			max_fit, min_fit = utility.min_max_member_fitness(pop_list)
			#~ utility.print_member_fitness(pop_list)
			reset_start = time.time()
			for mem in pop_list:
				#~ pprint(mem.FemurStructure.__dict__)
				if mem.total_fitness < 1:
					mem.reset_member()
				else:
					good_mem += 1
				#~ input(pprint(mem.FemurStructure.__dict__))
				flf.define_components(mem)
			fe.fitness_evaluation(pop_list)
			os.system('cls')
			reset_end = time.time()
			print("Percent Valid: " + str(good_mem/len(pop_list)*100) + "%")
			print("Time Elapsed: " + str(reset_end-reset_start))
			print("Reset Count: " + str(reset_count))
			reset_count += 1
		else:
			utility.print_member_fitness(pop_list)
			input("Valid generation. Any key to continue...")

	current_gen = 0

	while current_gen < generation_count:
		gen_start = time.time()
		total_fitness = fe.fitness_evaluation(pop_list)
		roulette.evaluate(pop_list)
		
		print("\nPopulation size: " + str(len(pop_list)) + '\n')
		print("Current Generation: " + str(current_gen))
		max_fitness,min_fitness = utility.min_max_member_fitness(pop_list)
		print("Max Fitness: " + str(max_fitness))
		print("Min Fitness: " + str(min_fitness))
		gen_end = time.time()
		print("Generation Time: " + str(gen_end-gen_start))
		print("Average Fitness: " + str(total_fitness/len(pop_list)) + '\n')
		
		pop_count_list.append(len(pop_list))
		max_fitness_list.append(max_fitness)
		total_fitness_list.append(total_fitness)
		current_gen += 1

	extf.export_generation_data(pop_count_list,max_fitness_list,total_fitness_list)
	end = time.time()
	print("Elapsed Time: " + str(end-start))
	cycle_count += 1
	setattr(PopMember,'is_initial_gen',True)
print("\n~~~~~~ Program End ~~~~~~\n")
