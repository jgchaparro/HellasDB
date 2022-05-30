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
from auxiliary_code.data_wrangling import unroll_census, extract_article
from auxiliary_code.utils import filenames

#%% Obtain census .xlsx

census_url = 'https://www.statistics.gr/documents/20181/1210503/Kallikratis_me_plithismous_1991_2011.xls/4b9f7484-fae7-44e2-852c-ec650dc0a5c8?version=1.0'
raw_census_filename = '../data/raw_data/raw_census.xls'

get_raw = False

# Retrieve census only if it does not exist
if not exists(raw_census_filename) or get_raw:
    urllib.request.urlretrieve(census_url, raw_census_filename)


#%% Read census

dfs = {}
dfs['raw'] = pd.read_excel(raw_census_filename)

#%% Clean census df

# Get rid of first rows
df = dfs['raw'].copy()
df = df[4:]

# Reaplce column names
df.columns = ['level', 'nuts1', 'nut2', 'code', 'location', 
              'legal11', 'facto11', 'legal01', 'facto01', 'legal91', 'facto91']

# Fill NaNs with 0. We assume that there is no population if there is no register
pop_cols = ['legal11', 'facto11', 'legal01', 'facto01', 'legal91', 'facto91']
df[pop_cols] = df[pop_cols].fillna(0)


#%% Prepare for unroll

# Retain only regional data
df = df[df['level'] >= 0]

# Add full codification: NUTS1 + NUT2 + CODE
df['full_code'] = df['nuts1'] + df['nut2'] + df['code']
df['full_code'] = df['full_code'].apply(lambda x: int(x))

# Add perifereia column
perif_edres = [df[df.level == 3]['location'].iloc[i].replace('ΠΕΡΙΦΕΡΕΙΑ ', '').split(' (') for i in range(len(df[df.level == 3]))]

#%% Unroll census

unroll_census(df)

#%% Select necessary rows

# Retain only towns (level = 8)
df = df[df['level'] == 8]

# Drop `level` column

df.drop(columns = 'level', inplace = True)

# Convert 'koinot_id' dtype
df['koinot_id'] = df['koinot_id'].apply(lambda x: int(x))

#%% Save checkpoint

dfs['cp1'] = df.copy()

#%% Change from katharevoussa to dimotiki Greek

# TODO: correct dimotiki functions

# =============================================================================
# df['original_name'] = df['location']
# df['namedata'] = df['location'].apply(dimotiki)
# df.reset_index(inplace = True, drop = True)
# namedata = pd.json_normalize(df['namedata'])
# 
# # Join df and clean 'namedata' column
# df = pd.concat([df, namedata], axis = 1)
# df.drop(columns = 'namedata', inplace = True)
# 
# # Reorder columns
# df['location'] = df['dim']
# df.drop(columns = 'dim', inplace = True)
# 
# =============================================================================

#%% Split location name and article

# Load checkpoint
df = dfs['cp1']

# Save original location name
df['original_location_name'] = df['location']

df['location'] = df['original_location_name'].apply(lambda x: x.split(',')[0])
df['article'] = df['original_location_name'].apply(extract_article)

#%% Create change columns

# De facto changes
# Total
df['total_change_facto_2001_2011'] = df['facto11'] - df['facto01'] 
df['total_change_facto_1991_2001'] = df['facto01'] - df['facto91']
df['total_change_facto_1991_2011'] = df['facto11'] - df['facto91'] 

# Percentage
df['perc_change_facto_2001_2011'] = np.round(((df['facto11'] - df['facto01']) * 100)/(df['facto01']), 2)
df['perc_change_facto_1991_2001'] = np.round(((df['facto01'] - df['facto91']) * 100)/(df['facto91']), 2)
df['perc_change_facto_1991_2011'] = np.round(((df['facto11'] - df['facto91']) * 100)/(df['facto91']), 2)

# Legal changes
# Total
df['total_change_legal_2001_2011'] = df['legal11'] - df['legal01'] 
df['total_change_legal_1991_2001'] = df['legal01'] - df['legal91']
df['total_change_legal_1991_2011'] = df['legal11'] - df['legal91']

# Percentage
df['perc_change_legal_2001_2011'] = np.round(((df['legal11'] - df['legal01']) * 100)/(df['legal01']), 2)
df['perc_change_legal_1991_2001'] = np.round(((df['legal01'] - df['legal91']) * 100)/(df['legal91']), 2)
df['perc_change_legal_1991_2011'] = np.round(((df['legal11'] - df['legal91']) * 100)/(df['legal91']), 2)

# Replace infs and NaNs
to_replace = 0
for col in ['perc_change_facto_2001_2011',
            'perc_change_facto_1991_2001',
            'perc_change_facto_1991_2011',
            'perc_change_legal_2001_2011',
            'perc_change_legal_1991_2001',
            'perc_change_legal_1991_2011']:
    df[col] = df[col].replace({np.inf : to_replace, 
                           np.nan : to_replace})

#%% Save final ELSTAT census dataframe

df.to_csv(f'../data/{filenames["ELSTAT_census"]}.csv', index = False)
df.to_excel(f'../data/{filenames["ELSTAT_census"]}.xlsx')