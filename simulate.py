import pandas as pd
import numpy as np


# Load files as data frames
def load_files(excel_workbook='LifeSciences.xlsx'):
	scenarios = pd.read_excel(excel_workbook, sheetname='scenarios', skiprows=1, 
		na_values=['NA'], index_col=0)
	simulation = pd.read_excel(excel_workbook, sheetname='simulation', 
		skiprows=1, na_values=['NA'])
	laboratories = pd.read_excel(excel_workbook, sheetname='laboratories', 
		skiprows=2, na_values=['NA'], index_col=0)
	fumehoods = pd.read_excel(excel_workbook, sheetname='fumehoods', skiprows=2, 
		na_values=['NA'], index_col=0)

	lab_scenarios = build_scenario_dict(laboratories, scenarios)
	hood_scenarios = build_scenario_dict(fumehoods, scenarios)
	
	return {'scenarios':scenarios, 'simulation':simulation, 
	'laboratories':lab_scenarios, 'fumehoods':hood_scenarios}


# Helper for making scenario dicts
def build_scenario_dict(df, scenarios):
	scenario_dict = dict()

	for scenario in scenarios.index:
		temp = df.copy()

		for parameter in [x for x in scenarios.columns if x != 'description']:
			if parameter in df.columns:
				how = scenarios[parameter][scenario]
				if how != 'as_is':
					if how.split(':')[0] == 'replace_all':
						temp[parameter] = len(temp)*[how.split(':')[1]]

		scenario_dict[scenario] = temp

	return scenario_dict


class fumehood():
	def __init__(self, hood_id, *args, **kwargs):
		for dictionary in args:
      		for key in dictionary:
        		setattr(self, key, dictionary[key])
	    for key in kwargs:
	      setattr(self, key, kwargs[key])
		
		self.hood_id = hood_id
		self.sash_percent = 0
		self.sash_height = 0
		self.sash_time = -1
		self.occupancy = False
		self.occupancy_time = -1
		self.flow = self.min_cfm

	def __str__(self):
  		return self.hood_id

	def update_sash(self, time, sash_percent):
		self.sash_time = time
		self.sash_percent = sash_percent
		self.sash_height = self.max_sash_height * self.sash_percent * 0.01

	def update_occupancy(self, time, occupied):
		self.occupancy_time = time
		self.occupied = occupied

	def compute_flow(self):
		if self.occupied:
			face_vel_cfm = self.face_vel_occupied * sash_height * 
				self.sash_width / 144
		else:
			face_vel_cfm = self.face_vel_unoccupied * sash_height * 
				self.sash_width / 144

		return np.min([self.max_cfm, np.max([self.min_cfm, face_vel_cfm])])


class laboratory():
	def __init__(self, lab_id, *args, **kwargs):
		for dictionary in args:
	      	for key in dictionary:
	        	setattr(self, key, dictionary[key])
		for key in kwargs:
		    setattr(self, key, kwargs[key])

		self.lab_id = lab_id
		fumehoods = {}
		self.occupancy_time = -1
		self.ach = -1
		self.min_flow = -1
		self.ach_time = -1
		self.occupied = False

	def __str__(self):
  		return self.lab_id

  	def update_occupancy(self, time, occupied):
		self.occupancy_time = time
		self.occupied = occupied

	def update_ach(self, time):
		self.ach_time
		if time.hour < ach_day_start or time.hour > ach_night_start:
			if self.occupied: self.ach = self.night_occupied_ach
			else: self.ach = self.night_unoccupied_ach
		else:
			if self.occupied: self.ach = self.day_occupied_ach
			else: self.ach = self.day_unoccupied_ach
		
		self.min_flow = self.ach * self.surface_area * self.ceil_height / 60 +
			self.additional_evac

	def update_all(self, time, lab_occupancy, sash_percents, hood_occupancies):
		update_occupancy(time, lab_occupancy)
		assert len(sash_heights) == self.num_hoods
		assert len(hood_occupancies) == self.num_hoods

		for hood in sash_percents:
			self.fumehoods[hood].update_sash(time, sash_percents[hood])
			self.fumehoods[hood].update_occupancy(time, hood_occupancies[hood])

	def compute_flow(self, time):
		update_ach(time)
		base_lab = 0
		equip_inc = 0
		sash_driven = 0

		hood_sum = 0
		hood_min = 0
		
		for hood in self.fumehoods:
			hood_sum += hood.compute_flow()
			hood_min += hood.min_cfm()
		
		hood_above_min = hood_sum - hood_min
		assert hood_above_min >= 0

		# TODO - vary equipment min / max
		if self.min_flow > self.additional_equipment_max + hood_sum:
			base_lab = self.min_flow
			equip_inc = 0
			sash_driven = 0
		elif self.min_flow > self.additional_equipment_max + hood_min:
			base_lab = self.min_flow
			equip_inc = 0
			sash_driven = self.additional_equipment_max + hood_sum - self.min_flow
			assert sash_driven > 0
		else:
			base_lab = self.min_flow
			equip_inc = self.additional_equipment_max + hood_min - self.min_flow
			sash_driven = hood_above_min

		return(base_lab, equip_inc, sash_driven)


# Generate lab occupancy


# Generate fumehood occupancy


# For debugging & validation

p = load_files()
hoods = p['fumehoods']
labs = p['laboratories']

if __name__ == '__main__':
	print 'processing...'
	params = load_files()
	print params['scenarios'].head()
	print [x for x in params['scenarios'].columns if x != 'description']
