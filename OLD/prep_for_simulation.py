# -*- coding: utf-8 -*-
"""
Created on Mon Oct 06 15:08:55 2014

@author: Marc
"""
#%% imports
import pandas as pd
import numpy as np
import pacal as pc

#%% constants
building = "wong"

#%% functions to load relevant csv files

def load_fumehoods(filename = 'fumehoods.csv'):
    """Loads hood metadata for future use"""
    return pd.read_csv(filename).set_index('hood_id')

def load_laboratories(filename = 'laboratories.csv'):
    """Loads laboratory metadata for furture use"""
    return pd.read_csv(filename).set_index('lab_id')

def load_densities(filename = 'sash_densities.csv'):
    return pd.read_csv(filename)

#%% load
fumehoods = load_fumehoods()
laboratories = load_laboratories()
sash_densities = load_densities()




