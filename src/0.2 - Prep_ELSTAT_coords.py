# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
import urllib.request
from os.path import exists 
from utils import filenames

#%% Obtain census .csv

census_url = 'https://geodata.gov.gr/geoserver/wfs/?service=WFS&version=1.0.0&request=GetFeature&typeName=geodata.gov.gr:f45c73bd-d733-4fe0-871b-49f270c56a75&outputFormat=csv&srsName=epsg:3857'
raw_census_filename = '../data/raw_data/census_coord.csv'

get_raw = False

# Retrieve census only if it does not exist
if not exists(raw_census_filename) or get_raw:
    urllib.request.urlretrieve(census_url, raw_census_filename)

#%% Read census

dfs = {}
dfs['raw'] = pd.read_csv(raw_census_filename)

#%% Clean df

df = dfs['raw']

# Select necessary columns
sel_cols = ['NAME_OIK', 'NAMEF_OIK', 'lat', 'lon', 'h', 
            'NAME_DIAM', 'NAME_OTA', 'NAME_NOM', 'NAME_GDIAM']
df = df[sel_cols]

# Rename cols
ren_cols = ['name', 'full_name', 'lat', 'lon', 'h', 'dimenot', 'dimos', 
            'nomos', 'diam']
df.columns = ren_cols

# Replace 'A

rep_cols = ['name', 'full_name', 'dimenot']
for c in rep_cols:
    df[c] = df[c].str.replace('¶', 'Ά')

#%% Clean columns

df['full_name'] = df['full_name'].str.replace(', ', ',')
df['dimenot'] = df['dimenot'].str.replace('Τ.Δ.', '')
df['dimos'] = df['dimos'].str.replace('ΔΗΜΟΣ ', '')
df['dimos'] = df['dimos'].str.replace('ΚΟΙΝΟΤΗΤΑ ', '')
df['nomos'] = df['nomos'].str.replace('ΝΟΜΟΣ ', '')

#%% Save csv

df.to_csv(f'../data/{filenames["ELSTAT_coord"]}.csv', index = False)
df.to_excel(f'../data/{filenames["ELSTAT_coord"]}.xlsx')