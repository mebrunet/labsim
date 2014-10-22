import pandas as pd
import numpy as np

# Load files
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


# For debugging & validation

p = load_files()
hoods = p['fumehoods']

if __name__ == '__main__':
	print 'processing...'
	params = load_files()
	print params['scenarios'].head()
	print [x for x in params['scenarios'].columns if x != 'description']
