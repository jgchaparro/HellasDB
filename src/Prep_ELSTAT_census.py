# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
import urllib.request
import numpy as np
from os.path import exists 
from functions import unroll_census, dimotiki, filenames

#%% Obtain census .xlsx

census_url = 'https://www.statistics.gr/documents/20181/1210503/Kallikratis_me_plithismous_1991_2011.xls/4b9f7484-fae7-44e2-852c-ec650dc0a5c8?version=1.0'
raw_census_filename = '../data/raw_census.xls'

# Retrieve census only if it does not exist
if not exists(raw_census_filename):
    urllib.request.urlretrieve(census_url, raw_census_filename)

#%% Read census

dfs = {}
dfs['raw'] = pd.read_excel(raw_census_filename)

#%% Clean census df

# Get rid of first rows
df = dfs['raw'].copy()
df = df[4:]

# Reaplce column names
df.columns = ['level', 'nuts1', 'nut2', 'code', 'desc', 
              'iure11', 'facto11', 'iure01', 'facto01', 'iure91', 'facto91']

# Fill NaNs with 0. We assume that there is no population if there is no register
pop_cols = ['iure11', 'facto11', 'iure01', 'facto01', 'iure91', 'facto91']
df[pop_cols] = df[pop_cols].fillna(0)


#%% Prepare for unroll

# Drop bigger administrative units rows
df = df[df['level'] >= 3]

# Add perifereia column
perif_edres = [df[df.level == 3]['desc'].iloc[i].replace('ΠΕΡΙΦΕΡΕΙΑ ', '').split(' (') for i in range(len(df[df.level == 3]))]

#%% Unroll census

unroll_census(df)

#%% Add full codification: NUTS1 + NUT2 + CODE

df['code'] = df['nuts1'] + df['nut2'] + df['code']
df['code'] = df['code'].apply(lambda x: int(x))

# Retain only towns (level = 8)
df = df[df['level'] == 8]

# Drop unneeded code columns
df = df.iloc[:, 3:]

#%% Change from katharevoussa to dimotiki Greek

df['namedata'] = df['desc'].apply(dimotiki)
df.reset_index(inplace = True, drop = True)
namedata = pd.json_normalize(df['namedata'])

# Join df and clean 'namedata' column
df = pd.concat([df, namedata], axis = 1)
df.drop(columns = 'namedata', inplace = True)

# Reorder columns
df['desc'] = df['dim']
df.drop(columns = 'dim', inplace = True)

#%% Save final ELSTAT census dataframe

df.to_csv(f'../data/{filenames["ELSTAT_census"]}.csv', index = False)
df.to_excel(f'../data/{filenames["ELSTAT_census"]}.xlsx')