# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
from utils import filenames

#%% Load data

df = pd.read_csv(f'../final_databases/{filenames["full_database"]}.csv', index_col = 'index')
