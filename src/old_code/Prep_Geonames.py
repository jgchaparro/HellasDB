# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
import numpy as np

from os.path import exists 

from functions import retrieve_API_info, get_greek_name, translits, \
                    dimotiki_simp, filenames

#%% Set database csv path

raw_gn_csv_path = '../data/raw_geonames_df.csv'

#%% Get raw data

get_raw = False

if get_raw or not exists(raw_gn_csv_path): # Obtain fresh data
    dfgn = retrieve_API_info(raw_gn_csv_path)
    from_csv = False
else: # Use existing database
    dfgn = pd.read_csv(raw_gn_csv_path)
    from_csv = True

#%% First steps processing Geonames df

# Drop unneeded columns
dropcols = ['astergdem', 'fcl', 'srtm3', 'score', 'countryCode', 'fcode',
            'continentCode', 'fclName', 'countryName', 'fcodeName',
            'timezone.gmtOffset', 'timezone.timeZoneId', 'timezone.dstOffset',
            'bbox.accuracyLevel', 'adminCodes2.ISO3166_2', 'adminCodes1.ISO3166_2',
            'cc2', 'countryId', 'adminName4', 'adminName5',
            'bbox.east', 'bbox.south', 'bbox.north', 'bbox.west',
            'geonameId'
            ]

dfgn.drop(columns = dropcols, inplace = True)

# Remove 'Unnamed: 0' column generated when reading .csv
if from_csv: 
    dfgn.drop(columns = 'Unnamed: 0', inplace = True)

# Remove duplicates
dfgn.drop_duplicates(inplace = True)

#%% Create `nomos` column to replace adm2 column in Geonames
### It helps disambiguating when joining the census and Geonames

# Create column and replacing
dfgn['nomos'] = dfgn['adminName2']

for k, v in translits.items():
    dfgn.replace(k, v, inplace = True)
    
dfgn['nomos'].replace('', np.nan, inplace = True)

# Other preprocessing
dfgn['greek_name'].fillna('--ΑΓΝΩΣΤΟΣ--', inplace = True)

#%% Save processed Geonames dataframe and excel

dfgn.to_csv(f'../data/{filenames["Geonames"]}.csv', index = False)
dfgn.to_excel(f'../data/{filenames["Geonames"]}.xlsx')