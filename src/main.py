# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd

from functions import filenames, merge_census_gn, merge_census_urban

#%% Load data

dfs = {'census' : pd.read_csv(f'../data/{filenames["ELSTAT_census"]}.csv'),
       'geonames' : pd.read_csv(f'../data/{filenames["Geonames"]}.csv'),
       'urban' : pd.read_csv(f'../data/{filenames["ELSTAT_urban"]}.csv').set_index('code')}

#%% Select base df

df = dfs['census'].copy()

#%% Merge ELSTAT census and Geonames

merge_census_gn(df, dfs['geonames'])

# Present merging results
n_crossed = len(df[~df['lat'].isnull()])
print(f'{str(n_crossed)} coordinates added')

#n_elevs = len(df[~df['elev'].isnull()])
#print(f'{str(n_elevs)} elevations added')

#%% Save intermediate df

df.to_csv('../data/census+geonames.csv', index = False)

#%% Merge main df and ELSTAT urban

merge_census_urban(df, dfs['urban'])

#%% Save final .csv

df.to_csv(f'../final_databases/{filenames["full_database"]}.csv', index = False)
df.to_excel(f'../final_databases/{filenames["full_database"]}.xlsx')
