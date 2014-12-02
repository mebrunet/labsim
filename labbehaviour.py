'''
TODO:

- Sash height from file

'''

import pandas as pd
import numpy as np
from scipy import stats

densities = pd.read_csv('rvs/densities.csv')
parse_list = lambda x: np.array(map(float,x[1:-1].split()))
rv_func = lambda pk: stats.rv_discrete(values=(range(0,100,5),5 * parse_list(pk)))
densities['rv'] = densities.density.map(rv_func)
density_by_group = densities.groupby('group')

class sashrv():
	def __init__(self, profile_type):
		if profile_type in ('very_low', 'low', 'mid', 'high', 'very_high'):
			self.profile_type = profile_type
			self.density_by_time = density_by_group.get_group(profile_type).groupby(['hour', 'weekend'])
		else:
			# Case where sash height constant
			try:
				self.sash_height = int(profile_type)
				self.profile_type = 'constant'
			except:
				# Case where sash hight from file
				pass

	def poll(self, time):
		if self.profile_type == 'constant':
			return self.sash_height
		else:
			rv = self.density_by_time.get_group((time.hour, time.weekday() >= 5))['rv'].iloc[0]
			return rv.rvs() + 5 * np.random.ranf()