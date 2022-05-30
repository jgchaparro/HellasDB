# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
import urllib.request
from os.path import exists
from auxiliary_code.utils import filenames

#%% Obtain corresp .xlsx

census_url = 'http://geodata.gov.gr/dataset/46f42d38-df48-4ffa-95ff-24032f4f4618/resource/772f6914-dfb4-48cd-8b22-c3e37b90de81/download/antistoixhshotakapodistriaskallikraths.xls'
raw_corresp_filename = '../data/raw_data/correspondence-kallikratis-kapodistrias.xls'

get_raw = False

# Retrieve census only if it does not exist
if not exists(raw_corresp_filename) or get_raw:
    urllib.request.urlretrieve(census_url, raw_corresp_filename)
    
#%% Read document

dfs = {}
dfs['raw'] = pd.read_excel(raw_corresp_filename, sheet_name = 'ΚΑΛΛΙΚΡ ΚΟΙΝΟΤΗΤΕΣ ',
                           header = 1)

#%% Clean df

df = dfs['raw'].copy()

# Select necessary columns
col_index = [6, 10, 12, 14, 19, 21, 23]
df = df.iloc[:, col_index]

col_names = ['dimenot_kal', 'dimos_kal', 'nomos_kal', 'perifereia_kal',
             'dimos_kap', 'nomarchia_kap', 'perifereia_kap']

df.columns = col_names

df.drop_duplicates(inplace = True)

#%% Save df

df.to_csv(f'../data/{filenames["Kal-Kap"]}.csv', index = False)
df.to_excel(f'../data/{filenames["Kal-Kap"]}.xlsx')