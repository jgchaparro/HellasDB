# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd

from functions import merge_census_coord, merge_census_urban, merge_agion_oros, \
                        merge_simple, reverse_merging
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

merge_census_coord(df, dfs['coord'], dfs['Kal-Kap'])

# Present merging results
n_coord = len(df[~df['lat'].isnull()])
print(f'{str(n_coord)} coordinates added')
 
n_elevs = len(df[~df['h'].isnull()])
print(f'{str(n_elevs)} elevations added')
 
print(f'Elapsed time: {time.time() - start}')
 

#%% Save intermediate df

df.to_csv('../data/census+coord.csv', index = False)

#%% Load intermediate

df = pd.read_csv('../data/census+coord.csv')

#%% Merge secondary NaNs

merge_agion_oros(df, dfs['coord'])
merge_simple(df, dfs['coord'])

#%% Reverse merging

reverse_merging(df, dfs['coord'])

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



#%% Tests

 
# print(len(df[df.lat.isnull()]))
# df_nans = df[df.lat.isnull()]
# 
# dfc = dfs['coord']
# 
# for town in df_nans['original_name']:
#     res = df[df['original_name'] == town]
#     if len(res) == 1:
#         print(res)
# 
# df['lat+long'] = [(lat, long) for lat, long in zip(df['lat'], df['long'])]
# dfc['lat+long'] = [(lat, long) for lat, long in zip(dfc['lat'], dfc['lon'])]
# 
# dfc['used'] = False
# dfc['used'] = [True if r in df['lat+long'].tolist() else False for r in dfc['lat+long'].tolist()]
# 
# #%% Unused codes
# 
# 
# 
# for town in df_nans['original_name']:
#     res = df[df['original_name'] == town]
#     if len(res) == 1:
#         print(res)
# 
# =============================================================================
