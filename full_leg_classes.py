""" This file contains the class structures and hierarchy for
	the full-leg replacement prosthetic model, starting at
	the population level and working down through 
	population member, to components, to component
	factors such as stress, deflection, and other
	analysis functions."""
import random, math, os
import utility_functions as utility
import extfile_functions as extf
from __main__ import material_location, force_location, client_location
from pprint import pprint

#~ class Force():
	#~ pass
	
# 				--- Population Member ---
class PopMember():
	"""Class containing all the information for a single population member. Initializes all the other subclasses per this design."""
	
	# Set class variables
	next_mem = 0
	is_initial_gen = True
	
	material_list, mat_names, unit_list = extf.build_material_list(material_location)
	client_info = extf.import_client_info(client_location)
	
	def __init__(self):
		next_mem = 0
		next_mem += 1
		
		# Initialize  member characteristics, increment class variable next_mem
		self.mem_id = next_mem
		self.age = -3
		# >>> Change if components are added to the design. Error checking variable <<<
		self.comp_count = 19
		next_mem += 1
		
		# Initialize evaluation variables and classes
		self.total_fitness = 0
		self.total_mass = 0
		self.total_cost = 0
		
		# Initialize boolean values
		self.is_valid = True
		self.is_defined = False
		self.is_evaluated = False
		
		# Initialize Structure members
		self.FemurStructure =  Structure()
		self.TibiaStructure =  Structure()
		#~ self.FootStructure =  FootStructure()
		
		# Initialize Gimbal members
		self.HipGimbal =  Gimbal()
		self.KneeGimbal =  Gimbal()
		self.AnkleGimbal =  Gimbal()
		
		# Initialize Cylinder members
		self.AnkleAbductCylinder = Cylinder()
		self.AnkleAdductCylinder = Cylinder()
		self.AnkleExtendCylinder = Cylinder()
		self.AnkleFlexCylinder = Cylinder()
		self.AnkleInternalCylinder = Cylinder()
		self.AnkleExternalCylinder = Cylinder()
		self.HipAbductCylinder = Cylinder()
		self.HipAdductCylinder = Cylinder()
		self.HipExtendCylinder = Cylinder()
		self.HipFlexCylinder = Cylinder ()
		self.KneeExtendCylinder = Cylinder()
		self.KneeFlexCylinder = Cylinder()
		self.MainCylinder = MainCylinder()
		self.ReceiverCylinder = ReceiverCylinder()
	
		# Build reference dictionary, and check for correct number of components
		self.define_component_list()
		if len(self.component_dict) < self.comp_count:
			print("Dictionary Length: " + str(len(self.component_dict)))
			print("Component Count: " + str(self.comp_count))
			input("Component Dictionary Length Error")
		
		# Apply name variables to each component
		for comp_name,comp in self.component_dict.items():
			comp.name = comp_name
			comp.define_forces()
	
	def reset_member(self):
		for comp_name, comp in self.component_dict.items():
			#~ pprint(comp.__dict__)
			comp.get_new_values()
			#~ input(pprint(comp.__dict__))
			self.is_defined = False
			self.is_evaluated = False
		self.define_component_list()
			
	def define_component_list(self):
		self.component_dict = {}
		# >>> Modify with added components <<<
		component_types = ['Cylinder', 'Gimbal', 'Structure']
		for n in self.__dict__:
			for comp_type in component_types:
				if comp_type in n:
					self.component_dict[n] = self.__dict__[n]
	
	def assign_genome(self,genome_info):
		self.define_component_list()
		for comp_name,gen_info in genome_info.items():
			self.component_dict[comp_name].binary_decode(gen_info[0],gen_info[1])
		for comp_name,comp in self.component_dict.items():
			comp.define_component_variables()		
		
#				 --- Evaluation Classes ---
class Deflection():
	pass

class MaterialProperties():
	""" Stores material property data for a component. """
	
	def __init__(self,material_list,material_ID):

		MatProperties = {}
		# Cycles through material list looking for a matching name value
		for entry in material_list:
			if int(entry['id']) == material_ID:
				for k,v in entry.items():
					if k == 'ID':
						continue
					MatProperties[k] = v
		
		self.name = MatProperties['name']
		self.treatment = MatProperties['treatment']
		self.cost = MatProperties['cost']
		self.density = MatProperties['density']
		self.ultimate_tensile_strength = MatProperties['ultimate_tensile_strength']
		self.yield_strength = MatProperties['yield_strength']
		self.elastic_modulus = MatProperties['elastic_modulus']
		self.poissons_ratio = MatProperties['poissons_ratio']

# 				--- Design Classes ---

class Component(object):
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		self.stress = {}	
	
	def get_new_values(self):
		for var_name, var in self.variable_dict.items():
			#~ print(var_name)
			#~ print(self.__dict__[var_name])
			self.__dict__[var_name] = random.randint(1,63)
			self.define_component_variables()
	
	def define_forces(self):
		self.force = extf.import_forces(force_location,self.name)
		
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		genome = []
		encode_key = {}
		key_index = 0
		for name,var in self.variable_dict.items():
			encode_key[key_index]=name
			key_index += 1
			for n in utility.binary_encode(var):
				genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(genome)/6 == self.var_count):
			print("\n Encode Key:\n")
			pprint(encode_key)
			print("\nVariable Dictionary: \n")
			pprint(self.variable_dict)
			print("Genome Length: " + str(len(genome)))
			print("Variables: " + str(self.var_count))
			input("Binary Encode Genome Length Error")

		return genome, encode_key
	
	def binary_decode(self, new_genome,key):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
		# Separate dictionary terms into separate variables
		#~ for n,i in new_genome.items():
			#~ genome = i
		
		# Split into 6-bit chromosomes
		i = 0
		chrom_num = -1
		temp_chrom = [0]*6
		chrom_list = [[]] * self.var_count
		
		while i <= len(new_genome):
			if  i == len(new_genome):
				chrom_num += 1
				chrom_list[chrom_num] = temp_chrom
				break
			elif i % 6 == 0 and i != 0:
				chrom_num += 1
				chrom_list[chrom_num]=(temp_chrom)
				temp_chrom = [0] * 6
			temp_chrom[(i%6)] = new_genome[i]
			i += 1
		
		# Check to ensure genome is correct length
		if len(chrom_list) != self.var_count:
			print("Chromosome List Length: " + str(len(chrom_list)))
			print("Variables: " + str(self.var_count))
			input("Binary Decode Chromosome List Error")
		
		# Assign correct binary value to correct variable
		binary_dict = {}
		for i,name in key.items():
			binary_dict[name] = chrom_list[int(i)]
		
		val_dict = {}
		for name,val in binary_dict.items():
			val_dict[name] = utility.binary_decode(val)		
		
		# Assign decoded values to non-calculated variables
		for name, var in self.variable_dict.items():
			self.__dict__[name] = val_dict[name]

	def define_component_variables(self):
		self.variable_dict = {}
		# >>> Modify with changes in component non-design variables.
		variable_types = ['force','stress','var_count','material_ID','Material','Chance','dict','structure','name','calc','fitness','safety','valid']
		for n in self.__dict__:
			is_valid = True
			for var_type in variable_types:
				if var_type in n:
					is_valid = False
					break
			if is_valid == True:
				self.variable_dict[n] = self.__dict__[n]

	def roulette_chance(self):
		self.XoverChance = [0] * (self.var_count * 6 )
		self.MutateChance = [0] * (self.var_count * 6 )
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
	

class Cylinder(Component):
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 

		# >>> Change if variables added or removed <<<
		self.var_count = 4
		self.roulette_chance()
							
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
						
			self.inner_diameter = random.randint(1,20)
			self.cyl_length = random.randint(1,20)
			self.cyl_thickness = random.randint(1,20)
			self.base_thickness = random.randint(1,20)
			
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ''
			
			self.inner_diameter =0
			self.cyl_length = 0
			self.cyl_thickness = 0
			self.base_thickness = 0
		self.calculated_variables()
		self.define_component_variables()
		
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		try:	
			self.calc_r_head = self.inner_diameter
		except AttributeError:
			self.calc_r_head = self.calc_inner_diameter
	
class MainCylinder(Component):
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		# >>> CALCULATE MAX EXTERNAL CYL SIZE <<<
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		self.roulette_chance()
	
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
						
			self.inner_diameter = random.randint(1,20)
			self.cyl_length = random.randint(1,20)
			self.cyl_thickness = random.randint(1,20)
			self.base_thickness = random.randint(1,20)
			
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ''
			self.inner_diameter =0
			self.cyl_length = 0
			self.cyl_thickness = 0
			self.base_thickness = 0
		self.calculated_variables()
		self.define_component_variables()
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		try:	
			self.calc_r_head = self.inner_diameter
		except AttributeError:
			self.calc_r_head = self.calc_inner_diameter
		
class ReceiverCylinder(Component):
	""" Contains the design parameters for the receiver
		actuation cylinder member."""
		
	def __init__(self): 
		# >>> CALCULATE MAX EXTERNAL CYL SIZE <<<
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		self.roulette_chance()
		
		# Client Variables
		self.force = extf.import_forces(force_location,'ReceiverCylinder')
		self.stress = {}
			
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
						
			self.inner_diameter = random.randint(1,20)
			self.cyl_length = random.randint(1,20)
			self.cyl_thickness = random.randint(1,20)
			self.base_thickness = random.randint(1,20)
			
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ''
			self.inner_diameter =0
			self.cyl_length = 0
			self.cyl_thickness = 0
			self.base_thickness = 0
		self.calculated_variables()
		self.define_component_variables()			
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		try:	
			self.calc_r_head = self.inner_diameter
		except AttributeError:
			self.calc_r_head = self.calc_inner_diameter
		
class Structure(Component):
	""" Contains the design parameters for the femur
		structural member."""
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 11
		self.roulette_chance()
		
		# Client Variables
		self.structure_length = PopMember.client_info['FemurLength']
		self.stress = {}
			
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
			
			self.rib_width = random.randint(1,20)
			self.rib_length = random.randint(1,20)
			self.flange_width = random.randint(1,20)
			self.flange_thickness = random.randint(1,20)
			self.core_diameter = random.randint(1,20)
			self.core_inner_diameter = random.randint(1,20)
			self.core_thickness = random.randint(1,20)
			self.mount_thickness = random.randint(1,20)
			self.mount_width = random.randint(1,20)
			self.mount_modifier = random.randint(0,50)
			self.mount_peg_diameter = random.randint(1,10)
			
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ""
			self.rib_width = 0
			self.rib_length = 0
			self.flange_width = 0
			self.flange_thickness = 0
			self.core_diameter = 0
			self.core_inner_diameter = 0
			self.core_thickness = 0
			self.mount_thickness = 0
			self.mount_width = 0
			self.mount_modifier = 0
			self.mount_peg_diameter = 0
			
		self.define_component_variables()
		self.calculated_variables()
		
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:

		self.calc_flange_radius = math.sqrt(self.rib_length ** 2 + (self.flange_width/2)**2)
		self.calc_mount_width = (1 + self.mount_modifier/50) * self.mount_peg_diameter
		self.calc_mount_height =  1.5 * self.calc_mount_width
		
class Gimbal(Component):
	""" Contains the design parameters for the ankle 
		gimbal assembly (mounts, cross). """
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		self.roulette_chance()

		# Client variables
		self.stress = {}
		
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
						
			self.peg_length = random.randint(1,20)
			self.peg_diameter = random.randint(1,20)
			self.mount_modifier = random.randint(1,63)
			self.mount_thickness = random.randint(1,10)
	
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ""
			self.peg_length = 0
			self.peg_diameter = 0
			self.mount_modifier = 0
			self.mount_thickness = 0
		
		self.calculated_variables()
		self.define_component_variables()
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		self.calc_mount_width = (self.mount_modifier/100 + 1) * self.peg_diameter
		self.calc_mount_height =  1.5 * self.calc_mount_width

#class PistonHead(Component):
	#""" Contains the design parameters for the ankle 
		#gimbal assembly (mounts, cross). """
		
	#def __init__(self):
		
		## >>> Change if variables added or removed <<<
		#self.var_count = 
		#self.roulette_chance()

		## Client variables
		#self.stress = {}
		
		## Initialize variables
		#if getattr(PopMember,'is_initial_gen') == True:
			## Random Variables:
			#self.material_ID = random.randint(1,len(PopMember.material_list))
			#self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
			
		#elif getattr(PopMember,'is_initial_gen') == False:
			#self.Material = ""
			
		#self.calculated_variables()
		#self.define_component_variables()
			
	#def calculated_variables(self):
		#""" Calculates the dependent variables for the class"""
		## Calculated Variables:
		#self.calc_r_head

# ~~~ End ~~~
