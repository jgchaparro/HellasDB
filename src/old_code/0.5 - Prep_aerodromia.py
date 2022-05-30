# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""

#%% Notes

"""
This census serves only as a support for the main ELSTAT census table.
As such, minimal changes will be performed.
"""

#%% Import modules 

import pandas as pd
import urllib.request
import numpy as np
from os.path import exists 
from functions import unroll_census, dimotiki
from utils import filenames

#%% Get urban census

urban_url = 'http://www.statistics.gr/documents/20181/1204266/resident_population_urban_census2011.xls'
raw_urban_filename = '../data/raw_urban.xls'

# Retrieve census only if it does not exist
if not exists(raw_urban_filename):
    urllib.request.urlretrieve(urban_url, raw_urban_filename)


#%% Read urban census

dfu = pd.read_excel(raw_urban_filename)

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

#%% Save final ELSTAT urban census dataframe

dfu.to_csv(f'../data/{filenames["ELSTAT_urban"]}.csv', index = True)
dfu.to_excel(f'../data/{filenames["ELSTAT_urban"]}.xlsx')