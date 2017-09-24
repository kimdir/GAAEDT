""" This file contains the class structures and hierarchy for
	the full-leg replacement prosthetic model, starting at
	the population level and working down through 
	population member, to components, to component
	factors such as stress, deflection, and other
	analysis functions."""
import random, math
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
		self.age = 0
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
		
		# Initialize Structure members
		self.FemurStructure =  FemurStructure()
		self.TibiaStructure =  TibiaStructure()
		#~ self.FootStructure =  FootStructure()
		
		# Initialize Gimbal members
		self.HipGimbal =  HipGimbal()
		self.KneeGimbal =  KneeGimbal()
		self.AnkleGimbal =  AnkleGimbal()
		
		# Initialize Cylinder members
		self.AnkleAbductCylinder = AnkleAbductCylinder()
		self.AnkleAdductCylinder = AnkleAdductCylinder()
		self.AnkleExtendCylinder = AnkleExtendCylinder()
		self.AnkleFlexCylinder = AnkleFlexCylinder()
		self.AnkleInternalCylinder = AnkleInternalCylinder()
		self.AnkleExternalCylinder = AnkleExternalCylinder()
		self.HipAbductCylinder = HipAbductCylinder()
		self.HipAdductCylinder = HipAdductCylinder()
		self.HipExtendCylinder = HipExtendCylinder()
		self.HipFlexCylinder = HipFlexCylinder ()
		self.KneeExtendCylinder = KneeExtendCylinder()
		self.KneeFlexCylinder = KneeFlexCylinder()
		self.MainCylinder = MainCylinder()
		self.ReceiverCylinder = ReceiverCylinder()
	
		# Build reference dictionary, and check for correct number of components
		self.define_component_list()
		if len(self.component_dict) < self.comp_count:
			print("Dictionary Length: " + str(len(self.component_dict)))
			print("Component Count: " + str(self.comp_count))
			input("Component Dictionary Length Error")
		
	def define_component_list(self):
		self.component_dict = {}
		# >>> Modify with
		component_types = ['Cylinder', 'Gimbal', 'Structure']
		for n in self.__dict__:
			for comp_type in component_types:
				if comp_type in n:
					self.component_dict[n] = self.__dict__[n]
		

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

# >-- Cylinders --<

class HipAdductCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'HipAdductCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass	
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])
		
class HipAbductCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'HipAbductCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass	
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class HipFlexCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'HipFlexCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass	

	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class HipExtendCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'HipExtendCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass	
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class KneeFlexCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'KneeFlexCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class KneeExtendCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
				
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'KneeExtendCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass	
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class AnkleAdductCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'AnkleAdductCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass	
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class AnkleAbductCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'AnkleAbductCylinder')
		self.stress = {}
			
		# Initialize design variables
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])
	
class AnkleFlexCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * var_count
		self.MutateChance = [0] * var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'AnkleFlexCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])
	
class AnkleExtendCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'AnkleExtendCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass

	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])
	
class AnkleInternalCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'AnkleInternalCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])
	
class AnkleExternalCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'AnkleExternalCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class MainCylinder():
	""" Contains the design parameters for the main
		actuation cylinder member."""
		
	def __init__(self): 
		# >>> CALCULATE MAX EXTERNAL CYL SIZE <<<
		
		# >>> Change if variables added or removed <<<
		var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * var_count
		self.MutateChance = [0] * var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.force = extf.import_forces(force_location,'MainCylinder')
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

class ReceiverCylinder():
	""" Contains the design parameters for the receiver
		actuation cylinder member."""
		
	def __init__(self): 
		# >>> CALCULATE MAX EXTERNAL CYL SIZE <<<
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
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
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		pass
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
		
		for n in utility.binary_encode(self.inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.cyl_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.base_thickness):
			self.genome.append(n)
		
		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
	
		self.inner_diameter = utility.binary_decode(chrom_list[0])
		self.cyl_length = utility.binary_decode(chrom_list[1])
		self.cyl_thickness = utility.binary_decode(chrom_list[2])
		self.base_thickness = utility.binary_decode(chrom_list[3])

# >-- Structures --<
	
class FemurStructure():
	""" Contains the design parameters for the femur
		structural member."""
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 11
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.structure_length = PopMember.client_info['FemurLength']
		self.force = extf.import_forces(force_location,'FemurStructure')
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
			
		self.calculated_variables()
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:

		self._flange_radius = math.sqrt(self.rib_length ** 2 + (self.flange_width/2)**2)
		self._mount_width = (1 + self.mount_modifier/50) * self.mount_peg_diameter
		self._mount_height =  1.5 * self._mount_width
		
	
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
	
		for n in utility.binary_encode(self.rib_width):
			self.genome.append(n)
		for n in utility.binary_encode(self.rib_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.flange_width):
			self.genome.append(n)
		for n in utility.binary_encode(self.flange_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.core_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.core_inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.core_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_width):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_modifier):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_peg_diameter):
			self.genome.append(n)

		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
		self.rib_width = utility.binary_decode(chrom_list[0])
		self.rib_length = utility.binary_decode(chrom_list[1])
		self.flange_width = utility.binary_decode(chrom_list[2])
		self.flange_thickness = utility.binary_decode(chrom_list[3])
		self.core_diameter = utility.binary_decode(chrom_list[4])
		self.core_inner_diameter = utility.binary_decode(chrom_list[5])
		self.core_thickness = utility.binary_decode(chrom_list[6])
		self.mount_thickness = utility.binary_decode(chrom_list[7])
		self.mount_width = utility.binary_decode(chrom_list[8])
		self.mount_modifier = utility.binary_decode(chrom_list[9])
		self.mount_peg_diameter = utility.binary_decode(chrom_list[10])
	
class TibiaStructure():
	""" Contains the design parameters for the tibia
		structural member."""
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 10
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables
		self.structure_length = PopMember.client_info['FemurLength'] / PopMember.client_info['LegRatio']
		self.force = extf.import_forces(force_location,'TibiaStructure')
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
			self.mount_peg_diameter = random.randint(0,50)
			
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

		self.calculated_variables()
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		
		self._flange_radius = math.sqrt(self.rib_length ** 2 + (self.flange_width/2)**2)
		self._mount_width = (1 + self.mount_modifier/50) * self.mount_peg_diameter
		self._mount_height =  1.5 * self._mount_width

	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
	
		for n in utility.binary_encode(self.rib_width):
			self.genome.append(n)
		for n in utility.binary_encode(self.rib_length):
			self.genome.append(n)
		for n in utility.binary_encode(self.flange_width):
			self.genome.append(n)
		for n in utility.binary_encode(self.flange_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.core_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.core_inner_diameter):
			self.genome.append(n)
		for n in utility.binary_encode(self.core_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_thickness):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_width):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_modifier):
			self.genome.append(n)
		for n in utility.binary_encode(self.mount_peg_diameter):
			self.genome.append(n)

		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables
		self.rib_width = utility.binary_decode(chrom_list[0])
		self.rib_length = utility.binary_decode(chrom_list[1])
		self.flange_width = utility.binary_decode(chrom_list[2])
		self.flange_thickness = utility.binary_decode(chrom_list[3])
		self.core_diameter = utility.binary_decode(chrom_list[4])
		self.core_inner_diameter = utility.binary_decode(chrom_list[5])
		self.core_thickness = utility.binary_decode(chrom_list[6])
		self.mount_thickness = utility.binary_decode(chrom_list[7])
		self.mount_width = utility.binary_decode(chrom_list[8])
		self.mount_modifier = utility.binary_decode(chrom_list[9])
		self.mount_peg_diameter = utility.binary_decode(chrom_list[10])
		
class FootStructure():
	pass

# >-- Gimbals --<
	
class HipGimbal():
	""" Contains the design parameters for the hip 
		gimbal assembly (mounts, cross). """
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 6
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables:
		self.Force = extf.import_forces(force_location,'HipGimbal')
		self.stress = {}
		
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
						
			self.peg_length = random.randint(1,20)
			self.peg_diameter = random.randint(1,20)
			self.mount_modifier = random.randint(1,100)/100 + 1
			self.mount_thickness = random.randint(1,10)
	
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ""
			self.peg_length = 0
			self.peg_diameter = 0
			self.mount_modifier = 0
			self.mount_thickness = 0
		
		self.calculated_variables()
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		self._mount_width = self.mount_modifier * self.peg_diameter
		self._mount_height =  1.5 * self._mount_width

	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
	
		for n in utility.binary_encode(self.peg_length):
				self.genome.append(n)
		for n in utility.binary_encode(self.peg_diameter):
				self.genome.append(n)
		for n in utility.binary_encode(self.mount_modifier):
				self.genome.append(n)
		for n in utility.binary_encode(self.mount_thickness):
				self.genome.append(n)

		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables

		self.peg_length = utility.binary_decode(chrom_list[0])
		self.peg_diameter = utility.binary_decode(chrom_list[1])
		self.mount_modifier = utility.binary_decode(chrom_list[2])
		self.mount_thickness = utility.binary_decode(chrom_list[3])

class KneeGimbal():
	""" Contains the design parameters for the knee 
		gimbal assembly (mounts, cross). """
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 4
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client Variables:
		self.force = extf.import_forces(force_location,'KneeGimbal')
		self.stress = {}
		
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
						
			self.peg_length = random.randint(1,20)
			self.peg_diameter = random.randint(1,20)
			self.mount_modifier = random.randint(1,100)/100 + 1
			self.mount_thickness = random.randint(1,10)
	
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ""
			self.peg_length = 0
			self.peg_diameter = 0
			self.mount_modifier = 0
			self.mount_thickness = 0
		
		self.calculated_variables()
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		self._mount_width = self.mount_modifier * self.peg_diameter
		self._mount_height =  1.5 * self._mount_width
		
	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
	
		for n in utility.binary_encode(self.peg_length):
				self.genome.append(n)
		for n in utility.binary_encode(self.peg_diameter):
				self.genome.append(n)
		for n in utility.binary_encode(self.mount_modifier):
				self.genome.append(n)
		for n in utility.binary_encode(self.mount_thickness):
				self.genome.append(n)

		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables

		self.peg_length = utility.binary_decode(chrom_list[0])
		self.peg_diameter = utility.binary_decode(chrom_list[1])
		self.mount_modifier = utility.binary_decode(chrom_list[2])
		self.mount_thickness = utility.binary_decode(chrom_list[3])

class AnkleGimbal():
	""" Contains the design parameters for the ankle 
		gimbal assembly (mounts, cross). """
		
	def __init__(self):
		
		# >>> Change if variables added or removed <<<
		self.var_count = 6
		
		# Initialize chance variables
		self.XoverChance = [0] * self.var_count
		self.MutateChance = [0] * self.var_count
		for n in self.XoverChance:
			n = (random.randint(1,9)/10)
		for n in self.MutateChance:	
			n = (random.randint(1,3)/10)		
		
		# Client variables
		self.force = extf.import_forces(force_location,'AnkleGimbal')
		self.stress = {}
		
		# Initialize variables
		if getattr(PopMember,'is_initial_gen') == True:
			# Random Variables:
			self.material_ID = random.randint(1,len(PopMember.material_list))
			self.Material = MaterialProperties(PopMember.material_list,self.material_ID)
						
			self.peg_length = random.randint(1,20)
			self.peg_diameter = random.randint(1,20)
			self.mount_modifier = random.randint(1,100)/100 + 1
			self.mount_thickness = random.randint(1,10)
	
		elif getattr(PopMember,'is_initial_gen') == False:
			self.Material = ""
			self.peg_length = 0
			self.peg_diameter = 0
			self.mount_modifier = 0
			self.mount_thickness = 0
		
		self.calculated_variables()
			
	def calculated_variables(self):
		""" Calculates the dependent variables for the class"""
		# Calculated Variables:
		self._mount_width = self.mount_modifier * self.peg_diameter
		self._mount_height =  1.5 * self._mount_width

	def binary_encode(self):
		"""Encodes class variables into a binary string, storing the values in an instance variable"""
		
		# >>> Change with any design changes <<<
		self.genome = []
	
		for n in utility.binary_encode(self.peg_length):
				self.genome.append(n)
		for n in utility.binary_encode(self.peg_diameter):
				self.genome.append(n)
		for n in utility.binary_encode(self.mount_modifier):
				self.genome.append(n)
		for n in utility.binary_encode(self.mount_thickness):
				self.genome.append(n)

		# Check to ensure the genome is the correct length
		if not(len(self.genome)/6 == self.var_count):
			print("Genome Length: " + str(len(self.genome)))
			print("Variables: " + str(self.var_count))
			input("Genome Length Error")
	
	def binary_decode(self, new_genome):
		"""Splits a genome into chromosome segments, then decodes and assigns values. Used in generation of new members."""
		
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
			input("Chromosome List Error")
	
		# Assign decoded values to non-calculated variables

		self.peg_length = utility.binary_decode(chrom_list[0])
		self.peg_diameter = utility.binary_decode(chrom_list[1])
		self.mount_modifier = utility.binary_decode(chrom_list[2])
		self.mount_thickness = utility.binary_decode(chrom_list[3])

# ~~~ End ~~~
