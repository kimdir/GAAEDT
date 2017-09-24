"""Defines GA functions for interacting with external files"""
from pprint import pprint
import csv
import datetime

def assign_class_attr(location, class_dest, check_val):
	"""Assigns class attributes from an external .txt file"""
	
	with open(location,newline="") as file_object:
		
		line_list = []
		header_index = 0
			
		#Load lines from attribute file into memory
		for line in file_object:
			line_list.append(line.split())
			
		#Check each line for the correct header
		#Note: Returns index for first occurence if multiple occur
		for x, line in enumerate(line_list):
			try:
				if line_list[x][0] != "#" or line_list[x][1] != check_val:
					continue
				header_index = x
				break
			except IndexError:
				continue
			print("No header found")
		
		#Add attributes defaulted to 0 until a blank line is encountered
		i = 1
		attr_remain = True
		attr_count = 0
		while attr_remain == True:
			try:
				attr_holder = line_list[header_index + i]
			except IndexError:
				attr_remain = False
				attr_count -= 1
				continue
			if attr_holder == []:
				attr_remain = False
				attr_count -= 1
				continue
			setattr(class_dest,attr_holder[0],0)
			i += 1
			attr_count += 1
	return attr_count
	
def initialize_classes(location):
	"""Initialize all design components from an external file"""
	master_class_dict = {}
	# Define the master class list that is used to create the individual component classes
	with open(location,newline="") as file_object:
		for line in file_object:
			line_holder = line.split()
			try:
				if line_holder[0] != "#":
					continue
			except:
				continue
			#Write master list of design components with a .name 
			#variable to pass to subclasses
			des_comp_name = line_holder[1]
			master_class_dict[line_holder[1]] = type(line_holder[1],(),dict(name=des_comp_name))
			
	return master_class_dict

def variable_reader(location):
	"""Reads design variables from an external file, ignoring comments
		and empty lines"""	
	parameter_list = {}
	with open(location) as file_object:
		for line in file_object:
			line_reader = line.split()
			try:
				if line_reader[0] == '#' or line_reader[0] =='##':
					continue
			except IndexError:
				continue
			line_key = line_reader.pop(0)
			parameter_list[line_key] = 0
	return parameter_list	

def build_material_list(mat_location):
	"""Builds the list of material properties for selection from a .csv
	file located in the same directory."""
	import csv
	
	property_list = []
	material_list = []
	name_list = []
	
	with open(mat_location,newline='') as csvfile:
		materialreader = csv.reader(csvfile, delimiter=',')
		property_list=[]		
		
		for i,row in enumerate(materialreader):
			
			# Assign property list categories, by setting all lowercase 
			# and replacing spaces with underscores
			if i == 0:
				for label in row:
					label_name = ''
					label_split = label.split()
					
					# Cycle through all words of a label and concatenate
					x = 0
					while x < len(label_split):
						label_name += label_split[x].lower()
						x += 1
						
						# Add _ if not last word
						if x != len(label_split):
							label_name += '_'
					property_list.append(label_name)
					# Check material information labels
					#~ print(label_name)
			
			# Define the units list for each material parameter
			elif i == 1:
				unit_list = []
				for val in row:
					if not val:
						unit_list.append('')
						continue
					unit_list.append(val)
			
			# Skip label rows
			elif row[0].startswith('#'):
				continue
			
			# Build the material dictionary for all values
			else:
				material_dict = {}
				for n,val in enumerate(row):
					if n > 0:
						try:
							material_dict[property_list[n]] = float(val)
							continue
						except ValueError:
							material_dict[property_list[n]] = val
							continue
					material_dict[property_list[n]] = val
				material_list.append(material_dict)
	return material_list,name_list,unit_list

def import_forces(location,component_name):
	"""Reads force names and values from an external file, ignoring 
		comments and empty lines. Returns dictionary of forces and 
		pressure with corresponding names."""	
	force_list = {}
	comp_match = False
	with open(location) as file_object:
		for line in file_object:

			# Skip blank lines
			try:
				line_reader = line.split()
				check = line_reader[0]
			except IndexError:
				if comp_match == True:
					break
				continue
			
			# If title found, add values
			if comp_match == True:
				line_key = line_reader.pop(0)
				force_list[line_key] = int(line_reader[-1])
				continue
			
			# Check for corresponding title
			if line_reader[0] != '#':
				continue
			elif line_reader[1] != component_name:
				continue
			elif line_reader[1] == component_name:
				comp_match = True
				continue
			else:
				input(">>> Component Match Error")

	return force_list

def import_client_info(location):
	client_info = {}
	
	with open(location,newline='') as csvfile:
		info_reader = csv.reader(csvfile, delimiter=',')		
		
		for row in info_reader:
			i = 0
			while i < len(row):
				# Check for labels
				if row[i].startswith('##'):
					break
				client_info[row[i]] = float(row[i+1])
				i += 2
	return client_info

def export_generation_data(pop_count_list, max_fitness_list, total_fitness_list):
	now = datetime.datetime.now()
	file_name = 'gen_data_' + str(now.month) + '-' + str(now.day) + '-' + str(now.year) +'_'+ str(now.hour) + str(now.minute)+'.csv'
	with open(file_name, 'x', newline = "") as csvfile:
		gen_info_writer = csv.writer(csvfile,dialect='excel')
		gen = 0
		gen_info_writer.writerow(['Generation']+['Population Count']+['Max Fitness']+['Total Fitness'])
		while gen < len(pop_count_list):
			temp_line = [gen]+[pop_count_list[gen]]+[max_fitness_list[gen]]+[total_fitness_list[gen]]
			gen_info_writer.writerow(temp_line)
			gen += 1
		gen_info_writer.writerow(['Data End'])
	
# ~~ End ~~
