# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd

from functions import merge_census_coord, merge_census_urban, filter_town_debug
from utils import filenames

import time


#%% Load data

dfs = {'census' : pd.read_csv(f'../data/{filenames["ELSTAT_census"]}.csv'),
       #'geonames' : pd.read_csv(f'../data/{filenames["Geonames"]}.csv'),
       'urban' : pd.read_csv(f'../data/{filenames["ELSTAT_urban"]}.csv').set_index('code'),
       'coord' : pd.read_csv(f'../data/{filenames["ELSTAT_coord"]}.csv')}

#%% Select base df

df = dfs['census'].copy()

#%% Debug census

filter_town_debug(90, dfs['census'], dfs['coord'])    

#%% Merge ELSTAT census and Geonames

start = time.time()

merge_census_coord(df, dfs['coord'])

# Present merging results
n_coord = len(df[~df['lat'].isnull()])
print(f'{str(n_coord)} coordinates added')
 
n_elevs = len(df[~df['h'].isnull()])
print(f'{str(n_elevs)} elevations added')
 
print(f'Elapsed time: {time.time() - start}')
 

#%% Save intermediate df

df.to_csv('../data/census+coord.csv', index = False)

#%% Merge main df and ELSTAT urban

start = time.time()

merge_census_urban(df, dfs['urban'])

# Present merging results
n_astikotita = len(df[~df['astikotita'].isnull()])
print(f'{str(n_astikotita)} cells added')

print(f'Elapsed time: {time.time() - start}') 
#%% Save final .csv

df.to_csv(f'../final_databases/{filenames["full_database"]}.csv', index = False)
df.to_excel(f'../final_databases/{filenames["full_database"]}.xlsx')
