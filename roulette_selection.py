""" Defines the roulette selection functions for the genetic algorithm,
including fitness conversion to selection probability, pairing, and 
new generation functions."""

import random, math
import utility_functions as utility
import genetic_algorithm_functions as gaf
from pprint import pprint

def age(pop_list):
	""" Checks for age-related member deaths, and increments age of 
		members that survive to the next generation. Returns modified 
		population list."""
	
	# Limit the number of members that can die per generation
	max_dead = math.floor(len(pop_list)/3)
	mem_dead = 0
		
	# Check for member death
	for i,member in enumerate(pop_list):
		thresh = random.randint(1,10)
		if member.age > thresh and mem_dead < max_dead:
			pop_list.pop(i)
			mem_dead += 1
		else:
			member.age += 1

			# If population member is older than 10 generations, kill the member
			if member.age > 10:
				pop_list.pop(i)
				mem_dead += 1
		
		# Adjust members dead to account for pair production
		mem_dead = math.floor(mem_dead/2)
		
	return pop_list, mem_dead
	
def fitness_convert(pop_list):
	""" Collects each member's fitness score, then gives a weighted 
		probability for selection. Returns a list composed of a lower
		and upper probability bound."""
	
	# Check for invalid members of the population
	add_temp = 0
	i = 0
	while i < len(pop_list):
		if pop_list[i].is_valid == False or pop_list[i].total_fitness == 0:
			pop_list.pop(i)
			add_temp += 1
		i += 1	
	
	#~ utility.print_member_fitness(pop_list)
	
	# Sum all fitness scores for weighting purposes.
	total_fitness = 0
	for member in pop_list:
		total_fitness += member.total_fitness
	
	print("Total Fitness Value: " + str(total_fitness))
	
	# Assign percentage of total fitness to each member
	fitness_percent = [0] * len(pop_list)
	for index,val in enumerate(pop_list):
		try:
			fitness_percent[index] = val.total_fitness/total_fitness
		except ZeroDivisionError:
			print(total_fitness)
			print("Dead population, ending program")
			exit()
			
	# Determine probability bounds for each member
	select_prob = []
	i = 0
	while i < len(pop_list):
		prob_range = [0,0]
		if i != 0:
			prob_range[0] = select_prob[(i-1)][1]
		prob_range[1] = prob_range[0] + fitness_percent[i]
		select_prob.append(prob_range)
		i += 1
	
	return select_prob, add_temp

def pairing(pop_list, select_prob, add_members):
	"""Takes selection probabilities and population list to define pairs
		of members for defining the new generations. Returns a list of 
		pairs for crossover."""
	# Consider adding dynamic population generation based on member 
	# deaths
	
	# Define the needed variables
	new_pairs = 8 + add_members
	#~ print('\nNew Pairs: ' + str(new_pairs) + '\n')
	current_pair = 0
	pair_list = []
	
	# Loop to determine new pairs
	while current_pair < new_pairs:
		pair_list.append(temp_pair_set(pop_list,select_prob))
		current_pair +=1
	return pair_list

def pair_search(select_prob):
	exit_val = False
	search_count = 0
	while exit_val == False:
		select_val = random.random()
		#~ print("Starting search...")
		for i,val in enumerate(select_prob):
			if (select_val >= val[0] and select_val < val[1]):
				exit_val = True
				return(i)
				exit()
			#~ print("No Append")

def temp_pair_set(pop_list,select_prob):
	temp_pair = [0,0]
	search_count = 0
	temp_pair[0] = pop_list[pair_search(select_prob)]
	temp_pair[1] = pop_list[pair_search(select_prob)]
	while temp_pair[0] == temp_pair[1]:
		#~ print("Bad Match. Repeating...")
		temp_pair[1] = pop_list[pair_search(select_prob)]
		search_count += 1
		#~ print(search_count)
		#~ if search_count == 100*len(pop_list):
			#~ print("Dead generation, ending program...")
			#~ exit()
	return temp_pair	

def new_gen (pop_list, pair_list):
	for pair in pair_list:
		mem1,mem2 = gaf.member_xover(pair[0],pair[1])
		pop_list.append(mem1)
		pop_list.append(mem2)
	return pop_list

def evaluate(pop_list):
	""" Performs evaluation of population fitness and generates new 
	members of the population based on roulette selection method. 
	Returns the updated population list."""
	
	add_members = 0
	
	# Kill old members
	pop_list,add_temp = age(pop_list)
	add_members += add_temp
	
	# Evaluate fitness scores and defines reproduction probabilty
	select_prob, add_temp = fitness_convert(pop_list)
	add_members += add_temp
	add_members /= 2

	# Roulette-select pairs for new generation members 
	pair_list = pairing(pop_list, select_prob,add_members)
	
	# Crosses pair members, then appends new members to population list
	pop_list = new_gen(pop_list, pair_list)
	
	return pop_list

# -End-
