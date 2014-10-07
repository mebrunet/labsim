# -*- coding: utf-8 -*-
"""
Created on Mon Oct 06 15:08:55 2014

@author: Marc
"""
#%% imports
import pandas as pd
import numpy as np

#%% constants
building = "wong"
num_weeks_to_sim = 52

#%% load relevant csv files

def load_fumehoods(filename = 'fumehoods.csv'):
    """Loads hood metadata for future use"""
    return pd.read_csv(filename).set_index('hood_id')

def load_laboratories(filename = 'laboratories.csv'):
    """Loads laboratory metadata for furture use"""
    return pd.read_csv(filename).set_index('lab_id')

#%% Generate timeseries data