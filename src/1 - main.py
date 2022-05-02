# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd

from functions import merge_census_coord, merge_census_urban, merge_agion_oros, \
                        reverse_merging, get_unused_lats, merge_parenthesis, \
                        merge_root_koinot_name, merge_simple, add_manual_locations, \
                            merge_dimos_name
from utils import filenames

import time


#%% Load data

dfs = {'census' : pd.read_csv(f'../data/{filenames["ELSTAT_census"]}.csv'),
       #'geonames' : pd.read_csv(f'../data/{filenames["Geonames"]}.csv'),
       'urban' : pd.read_csv(f'../data/{filenames["ELSTAT_urban"]}.csv').set_index('code'),
       'coord' : pd.read_csv(f'../data/{filenames["ELSTAT_coord"]}.csv'),
       'Kal-Kap' : pd.read_csv(f'../data/{filenames["Kal-Kap"]}.csv')}

#%% Select base df

df = dfs['census'].copy()

#%% Debug census

#filter_town_debug(90, dfs['census'], dfs['coord'])    

#%% Merge ELSTAT census and Geonames

start = time.time()

force = True

if force:
    merge_census_coord(df, dfs['coord'], dfs['Kal-Kap'])

# Present merging results
n_coord = len(df[~df['lat'].isnull()])
print(f'{str(n_coord)} coordinates added')
 
n_elevs = len(df[~df['h'].isnull()])
print(f'{str(n_elevs)} elevations added')
 
print(f'Elapsed time: {time.time() - start}')
 

#%% Save intermediate df

df.to_csv('../intermediate_databases/hellas_db_v0.1.csv', index = False)

#%% Load intermediate

df = pd.read_csv('../intermediate_databases/hellas_db_v0.1.csv')

#%% Merge secondary NaNs

merge_agion_oros(df, dfs['coord'])

#%% Reverse merging

reverse_merging(df, dfs['coord'])

#%% Merging parenthesis

merge_parenthesis(df, dfs['coord'], dfs['Kal-Kap'])

#%% Merge by name and koinotita

merge_root_koinot_name(df, dfs['coord'])

#%% Simple merge

#merge_simple(df, dfs['coord'])

#%% Merge by dimos and name

merge_dimos_name(df, dfs['coord'])

#%% Save intermediate df

df.to_csv('../intermediate_databases/hellas_db_v0.2.csv', index = False)

#%% Load intermediate

df = pd.read_csv('../intermediate_databases/hellas_db_v0.2.csv')

#%% Save location NaNs

# Census NaNs
nan_filepath = '../data/census_nans.xlsx'
dfs['nan'] = df[df['lat'].isnull()]
dfs['nan'].to_excel(nan_filepath)

# Unused coordinates
unused_lats_filepath = '../data/unused_coords.xlsx'
get_unused_lats(df, dfs['coord']).to_excel(unused_lats_filepath)

#%% Add manual locations

manual_locations_filename = '../data/manual_locations.xlsx'

add_manual_locations(df, manual_locations_filename)

#%% Save intermediate df

df.to_csv('../intermediate_databases/hellas_db_v0.3.csv', index = False)

#%% Load intermediate

df = pd.read_csv('../intermediate_databases/hellas_db_v0.3.csv')


#%% Merge main df and ELSTAT urban

start = time.time()

merge_census_urban(df, dfs['urban'])

# Present merging results
n_astikotita = len(df[~df['astikotita'].isnull()])
print(f'{str(n_astikotita)} cells added')

print(f'Elapsed time: {time.time() - start}') 

#%% Save final .csv

# Rename index
df.index.name = 'index'

df.to_csv('../intermediate_databases/hellas_db_v1.0.csv')
df.to_excel('../intermediate_databases/hellas_db_v1.0.xlsx')


#%% Tests
 
print(len(df[df.lat.isnull()]))
