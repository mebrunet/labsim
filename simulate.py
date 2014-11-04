''' 
TODO:

-Migrate all behavioral value generation to "labbehavior.py"
-Add mean or summary csv file to each scenario

'''



import pandas as pd
import numpy as np
from labbehaviour import sashrv

# Load files as data frames
class simulation():
	def __init__(self, excel_workbook='LifeSciences.xlsx'):
		self.excel_workbook = excel_workbook
		self.scenario_df = pd.read_excel(excel_workbook, sheetname='scenarios', 
			skiprows=1, na_values=['NA'], index_col=0)
		self.simulation_df = pd.read_excel(excel_workbook, sheetname='simulation', 
			skiprows=1, na_values=['NA'])
		self.laboratory_df = pd.read_excel(excel_workbook, sheetname='laboratories', 
			skiprows=2, na_values=['NA'], index_col=0)
		self.fumehood_df = pd.read_excel(excel_workbook, sheetname='fumehoods', 
			skiprows=2, na_values=['NA'], index_col=0)
		self.scenarios = {}

	 	self.time_rng = pd.date_range(start=self.simulation_df['start'][0], 
	 	end=self.simulation_df['end'][0], freq='H', tz='Canada/Eastern',
	 	name='time')

	 	self.load_scenarios()

	# Helper for making scenario dicts
	def build_scenario_dict(self, df, scenario_df):
		scenario_dict = dict()
		for scenario in scenario_df.index:
			temp = df.copy()
			for parameter in [x for x in scenario_df.columns if x != 'description']:
				if parameter in df.columns:
					how = scenario_df[parameter][scenario]
					if how != 'as_is':
						if how.split(':')[0] == 'replace_all':
							try: # try to parse as int first
								temp[parameter] = map(int, len(temp)*([how.split(':')[1]]))
							except:
								temp[parameter] = len(temp)*([how.split(':')[1]])
			scenario_dict[scenario] = temp
		return scenario_dict

	def load_scenarios(self):
		lab_df_dict = self.build_scenario_dict(self.laboratory_df, self.scenario_df)
		hood_df_dict = self.build_scenario_dict(self.fumehood_df, self.scenario_df)

		for name in self.scenario_df.index:
			self.scenarios[name] = scenario(name, self.time_rng, lab_df_dict[name], 
				hood_df_dict[name])

	def generate_time_series(self):
		for s in self.scenarios.values():
			s.generate_time_series(self.time_rng)

	def simulate(self, *args):
		if len(args) == 0:
			for s in self.scenarios.values():
				s.simulate()
		else:
			for s in args:
				self.scenarios[s].simulate()

	def summarize(self):
		writer = pd.ExcelWriter('summary.xlsx')
		for s in self.scenarios:
			self.scenarios[s].summarize().to_excel(writer, s)
		writer.save()


class scenario():
	def __init__(self, name, time_rng, lab_df, hood_df):
		self.name = name
		self.results = {}
		self.time_rng = time_rng
		self.laboratories = {}
		self.fumehoods = {}
		for lab in lab_df.index:
			self.laboratories[lab] = laboratory(lab, lab_df.loc[lab].to_dict())
		for hood in hood_df.index:
			self.fumehoods[hood] = fumehood(hood, hood_df.loc[hood].to_dict())
		for lab in self.laboratories.values():
			lab.associate_fumehoods(self.fumehoods)

	def generate_time_series(self, time_rng):
		for lab in self.laboratories:
			self.laboratories[lab].generate_time_series(time_rng,'ts\\'+self.name+'\\'+lab+'.csv')

	def simulate(self):
		for lab in self.laboratories:
			self.laboratories[lab].simulate('ts\\'+self.name+'\\'+lab+'.csv')

	def summarize(self):
		print self.name
		index = []
		result = {}
		result['base_lab'] =[]
		result['equip_inc'] = []
		result['sash_driven'] = []
		for lab in self.laboratories:
			print lab
			index.append(lab)
			df = pd.DataFrame.from_csv('ts\\'+self.name+'\\'+lab+'.csv')
			result['base_lab'].append(df['base_lab'].mean())
			result['equip_inc'].append(df['equip_inc'].mean())
			result['sash_driven'].append(df['sash_driven'].mean())
		df = pd.DataFrame(result, index = index)
		df.to_csv('ts\\'+self.name+'\\summary.csv')
		return df

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
		self.sashrv = sashrv(self.sash_profile)

	def __str__(self):
  		return self.hood_id

	def update_sash(self, time, sash_percent):
		self.sash_time = time
		self.sash_percent = sash_percent
		self.sash_height = self.max_sash_height * self.sash_percent * 0.01

	def update_occupancy(self, time, occupied):
		self.occupancy_time = time
		self.occupied = occupied

	def gen_occ(self, lab_occ):
		if lab_occ:
			if np.random.rand() < self.hood_use_rate:
				return True
			else: return False
		else: return False

	def gen_sash(self, time):
		return self.sashrv.poll(time)

	def compute_flow(self):
		if self.occupied:
			face_vel_cfm = self.face_vel_occupied * self.sash_height * self.sash_width / 144
		else:
			face_vel_cfm = self.face_vel_unoccupied * self.sash_height * self.sash_width / 144

		return np.min([self.max_cfm, np.max([self.min_cfm, face_vel_cfm])])


class laboratory():
	def __init__(self, lab_id, *args, **kwargs):
		for dictionary in args:
			for key in dictionary:
				setattr(self, key, dictionary[key])
		for key in kwargs:
			setattr(self, key, kwargs[key])

		self.lab_id = lab_id
		self.fumehoods = {}
		self.occupancy_time = -1
		self.ach = -1
		self.min_flow = -1
		self.ach_time = -1
		self.occupied = False

	def __str__(self):
  		return self.lab_id

  	def associate_fumehoods(self, hood_dict):
  		for hood in hood_dict.values():
  			if hood.lab_id == self.lab_id:
  				self.fumehoods[hood.hood_id] = hood

  	def update_occupancy(self, time, occupied):
		self.occupancy_time = time
		self.occupied = occupied

	def update_ach(self, time):
		self.ach_time
		if time.hour < self.ach_day_start.hour or time.hour > self.ach_night_start.hour:
			if self.occupied: self.ach = self.night_occupied_ach
			else: self.ach = self.night_unoccupied_ach
		else:
			if self.occupied: self.ach = self.day_occupied_ach
			else: self.ach = self.day_unoccupied_ach
		
		self.min_flow = self.ach * self.surface_area * self.ceil_height / 60 + self.additional_evac

	def update_all(self, time, lab_occupancy, sash_percents, hood_occupancies):
		self.update_occupancy(time, lab_occupancy)
		assert len(sash_percents) == len(self.fumehoods)
		assert len(hood_occupancies) == len(self.fumehoods)

		for hood in sash_percents:
			self.fumehoods[hood].update_sash(time, sash_percents[hood])
			self.fumehoods[hood].update_occupancy(time, hood_occupancies[hood])

	def generate_time_series(self, time_rng, filename):
		ts_dict = {'lab_occupancy':[]}
		for hood in self.fumehoods:
			ts_dict[hood+'-occ'] = []
			ts_dict[hood+'-sash'] = []

		for time in time_rng:
			lab_occ = self.gen_occ(time)
			ts_dict['lab_occupancy'].append(lab_occ)
			for hood in self.fumehoods:
				ts_dict[hood+'-occ'].append(self.fumehoods[hood].gen_occ(lab_occ))
				ts_dict[hood+'-sash'].append(self.fumehoods[hood].gen_sash(time))
		time_series_df = pd.DataFrame(ts_dict, index=time_rng)
		time_series_df.to_csv(filename)

	def gen_occ(self, time):
		if time.weekday >= 5: # weekend
			if time.hour < self.weekend_day_occupancy_start.hour or time.hour > self.weekend_night_occupancy_start.hour: # night
				if np.random.rand() < self.weekend_night_occupancy_rate:
					return True # occupied
				else: return False # unoccupied
			else: # day
				if np.random.rand() < self.weekend_day_occupancy_rate:
					return True # occupied
				else: return False # unoccupied
		else: # weekday
			if time.hour < self.day_occupancy_start.hour or time.hour > self.night_occupancy_start.hour: # night
				if np.random.rand() < night_occupancy_rate:
					return True # occupied
				else: return False # unoccupied
			else: # day
				if np.random.rand() < day_occupancy_rate:
					return True # occupied
				else: return False # unoccupied

	def compute_flow(self, time):
		self.update_ach(time)
		base_lab = 0
		equip_inc = 0
		sash_driven = 0

		hood_sum = 0
		hood_min = 0
		
		for hood in self.fumehoods.values():
			hood_sum += hood.compute_flow()
			hood_min += hood.min_cfm
		
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

	def simulate(self, filename):
		print "working on :" + filename
		df = pd.read_csv(filename, index_col = 0, parse_dates=True)
		df['base_lab'] = None
		df['equip_inc'] = None
		df['sash_driven'] = None
		for t in df.index:
			sash_percents = {}
			hood_occupancies ={}
			for hood in self.fumehoods:
				sash_percents[hood] = df[hood+'-sash'][t]
				hood_occupancies[hood] = df[hood+'-occ'][t]
			self.update_all(t, df.lab_occupancy[t], sash_percents, hood_occupancies)
			(df['base_lab'][t], df['equip_inc'][t], df['sash_driven'][t]) = self.compute_flow(t)
		df.to_csv(filename)





# For debugging & validation
'''
p = load_files()
hoods = p['fumehoods']
labs = p['laboratories']
'''
sim = simulation()
# sim.generate_time_series()
#sim.simulate()


if __name__ == '__main__':
	sim = simulation()
