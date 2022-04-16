# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
import requests as req
import urllib.request
import numpy as np

from functions import get_greek_name, dimotiki, translits, merge_census_gn

#%% Obtain census .xlsx

census_url = 'https://www.statistics.gr/documents/20181/1210503/Kallikratis_me_plithismous_1991_2011.xls/4b9f7484-fae7-44e2-852c-ec650dc0a5c8?version=1.0'
raw_census_filename = '../data/raw_census.xls'

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


#%% Unroll census df

# Drop bigger administrative units rows
df = df[df['level'] >= 3]

# Add perifereia column
perif_edres = [df[df.level == 3]['desc'].iloc[i].replace('ΠΕΡΙΦΕΡΕΙΑ ', '').split(' (') for i in range(len(df[df.level == 3]))]

adm_indices = {}
# Fill perifereia column
adm_name = 'perifereia'
df[adm_name] = np.nan
adm_indices[adm_name] = df.loc[df.level == 3].index
for i in adm_indices[adm_name]:
    df.loc[i, adm_name] = df.loc[i, 'desc'].replace('ΠΕΡΙΦΕΡΕΙΑ ', '').split(' (')[0]

# Fill nomos column
adm_name = 'nomos'
df[adm_name] = np.nan
adm_indices[adm_name] = df.loc[df.level == 4].index
for i in adm_indices[adm_name]:
    df.loc[i, adm_name] = df.loc[i, 'desc'].replace('ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ ', '').split(' (')[0]

# Fill dimos column
adm_name = 'dimos'
df[adm_name] = np.nan
adm_indices[adm_name] = df.loc[df.level == 5].index
for i in adm_indices[adm_name]:
    df.loc[i, adm_name] = df.loc[i, 'desc'].replace('ΔΗΜΟΣ ', '').split(' (')[0]
    
# Fill dimenot column
adm_name = 'dimenot'
df[adm_name] = np.nan
adm_indices[adm_name] = df.loc[df.level == 6].index
for i in adm_indices[adm_name]:
    df.loc[i, adm_name] = df.loc[i, 'desc'].split('ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ ')[-1]
    
# Fill koinot column
adm_name = 'koinot'
df[adm_name] = np.nan
adm_indices[adm_name] = df.loc[df.level == 7].index
for i in adm_indices[adm_name]:
    df.loc[i, adm_name] = df.loc[i, 'desc'].split('Κοινότητα ')[-1]

#%% Save df before inplaces

dfs['cp1'] = df.copy()

#%% Forward fill and clean

df = dfs['cp1']
df.ffill(inplace = True)

# Add full codification: NUTS1 + NUT2 + CODE
df['code'] = df['nuts1'] + df['nut2'] + df['code']
df['code'] = list(map(lambda x: int(x), df['code']))

# Retain only towns (level = 8)
df = df[df['level'] == 8]
df = df.iloc[:, 3:]

#%% Change from katharevoussa to dimotiki Greek

df['namedata'] = list(map(lambda x: dimotiki(x), df['desc']))
df.reset_index(inplace = True, drop = True)
namedata = pd.json_normalize(df['namedata'])

# Join df and clean 'namedata' column
df = pd.concat([df, namedata], axis = 1)
df.drop(columns = 'namedata', inplace = True)

# Reorder columns
df['desc'] = df['dim']
df.drop(columns = 'dim', inplace = True)

# Save checkpoint
dfs['cp2'] = df.copy()

#%% Get region bboxes from Geonames API

base_url = 'http://api.geonames.org/searchJSON?'

# Get all nomos
reg_gn = req.get(base_url, params = {
                                    'formatted' : 'true',
                                    'country' : 'GR',
                                    'fcode' : 'adm1',
                                    'username' : 'jgchaparro',
                                    'style' : 'full'}).json()['geonames']

# Get region bboxes. Exclude Mount Athos: not present in census.
reg_bbox = {r['name'] : r['bbox'] for r in reg_gn if r['name'] != 'Mount Athos'}

# Add path to Geonames .csv
gn_csv_path = '../data/raw_geonames_df.csv'

#%% Get towns for each region

rdfs = {} # Regional dataframes
for k, v in reg_bbox.items():
    print('Getting data for ' + k)
    
    # Get number of results for region
    params = {
            'east' : v["east"],
            'west' : v['west'],
            'north' : v['north'],
            'south' : v['south'],
            'country' : 'GR',
            'fcode' : 'PPL',
            'username' : 'jgchaparro',
            'style' : 'full',
            'maxRows' : 1,
            'startRow' : 0
            }
    n_results = req.get(base_url, params = params).json()['totalResultsCount']
    print('Number of results: ' + str(n_results))
    
    # Get number of iterations: Geonames API only allows max 6000 results
    # 1000 results per iteration, 1 extra for the rest
    rpp = 1000 # Rows per page
    params['maxRows'] = rpp
    iters = (n_results // params['maxRows']) + 1
    
    reg_json = []
    for _ in range(iters):
        partial_data = req.get(base_url, params = params).json()['geonames']
        reg_json.extend(partial_data)
        params['startRow'] += rpp
    
    towns = {r['name'] : r for r in reg_json}
    reg_df = pd.json_normalize(reg_json)
    rdfs[k] = reg_df

#%% Join all dfs and first steps cleaning Geonames df

dfgn = pd.concat([d for d in rdfs.values()]).reset_index().drop(columns = ['index'])

#%% Save dfgn to avoid retrieving data

# Change alternateName column to Greek to avoid losing data
dfgn['greek_name'] = [get_greek_name(x) for x in dfgn.alternateNames]
dfgn.drop(columns = 'alternateNames', inplace = True)

dfgn.to_csv(gn_csv_path)
print(f'Geonames dataframe saved in {gn_csv_path}')

#%% Load Geonames df

dfgn = pd.read_csv(gn_csv_path)

#%% First steps processing Geonames df

# Remove duplicates
dfgn.drop_duplicates(inplace = True)

# Drop unneeded columns
dropcols = ['astergdem', 'fcl', 'srtm3', 'score', 'countryCode', 'fcode',
            'continentCode', 'fclName', 'countryName', 'fcodeName',
            'timezone.gmtOffset', 'timezone.timeZoneId', 'timezone.dstOffset',
            'bbox.accuracyLevel', 'adminCodes2.ISO3166_2', 'adminCodes1.ISO3166_2',
            'cc2', 'countryId', 'adminName4', 'adminName5',
            'bbox.east', 'bbox.south', 'bbox.north', 'bbox.west']

dfgn.drop(columns = dropcols, inplace = True)

#%% Create `nomos` column to replace adm2 column in Geonames
### It helps disambiguating when joining the census and Geonames

# Create checkpoint
df = dfs['cp2']

# Create column and replacing
dfgn['nomos'] = dfgn['adminName2']

for k, v in translits.items():
    dfgn.replace(k, v, inplace = True)
    
dfgn['nomos'].replace('', np.nan, inplace = True)

#%% Preprocessing before merging

dfgn['greek_name'].fillna('--ΑΓΝΩΣΤΟΣ--', inplace = True)

# Create empty latitude, longitude and elevetion columns.
# They will be populated later
df[['lat', 'long', 'elev']] = np.nan

#%% Merging data from census and Geonames

merge_census_gn(df, dfgn)

# Present merging results
n_crossed = len(df[~df['lat'].isnull()])
n_elevs = len(df[~df['elev'].isnull()])
print(f'{str(n_crossed)} coordinates added')
print(f'{str(n_elevs)} elevations added')

#%% Save checkpoint

dfs['cp3'] = df.copy()

#%% Get urban census

urban_url = 'http://www.statistics.gr/documents/20181/1204266/resident_population_urban_census2011.xls'
raw_urban_filename = '../data/raw_urban.xls'

urllib.request.urlretrieve(urban_url, raw_urban_filename)

#%% Read urban census

dfs['urban_raw'] = pd.read_excel(raw_urban_filename)

dfu = dfs['urban_raw'].copy()

#%% Remove unnecessary headers

dfu = dfu[8:]

#%% Preprocess urban census

colnames = ['code', 'desc', 'mon_plith', 'astikotita', 'orinotita', 'ekt']
dfu.columns = colnames

# Drop empty columns
dfu.drop(dfu[dfu.code.isnull()].index, axis = 0, inplace = True)

dfu['code'] = list(map(lambda x: int(x), dfu['code']))
dfu.set_index('code', inplace = True)

#%% Change nomenclature for desired columns

# Change `astikotita` nomenclature:
dfu['astikotita'] = dfu['astikotita'].replace({'1': True, # Urban
                                               '2': False}) # Rural

# Change `orinotita`
dfu['orinotita'] = dfu['orinotita'].replace({'Π': 0, # Plains
                                             'Η': 1, # Semi-mountainous 
                                             'Ο': 2}) # Mountainous

#%% Add `astikotita` and `orinotita` data to main df

new_cols = ['astikotita', 'orinotita']
for col in new_cols:
    df[col] = np.nan

for i in df.index:
    try:
        code = int(str(df.loc[i, 'code'])[:-2])
        for col in new_cols:
            df.loc[i, col] = dfu.loc[code, col]
    except:
        print(f'Invalid code: i = {i}')

#%% Save final .csv

df.to_csv('../data/hellas_db.csv')