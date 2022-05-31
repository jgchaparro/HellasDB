# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 12:38:38 2022

@author: Jaime García Chaparro

"""
#%% Import modules 

import pandas as pd
from auxiliary_code.utils import filenames, island_adm
from auxiliary_code.data_adding import add_kapodistrias_adm, add_capital_data, \
                                        add_island_status

#%% Load dfs

dfs = {'census' : pd.read_csv(f'../data/{filenames["ELSTAT_census"]}.csv'),
       #'geonames' : pd.read_csv(f'../data/{filenames["Geonames"]}.csv'),
       'urban' : pd.read_csv(f'../data/{filenames["ELSTAT_urban"]}.csv').set_index('code'),
       'coord' : pd.read_csv(f'../data/{filenames["ELSTAT_coord"]}.csv'),
       'Kal-Kap' : pd.read_csv(f'../data/{filenames["Kal-Kap"]}.csv')}


#%% Load data

df = pd.read_csv('../intermediate_databases/hellas_db_v1.0.csv', index_col = 'index')

dfs['cp1'] = df.copy()

#%% Add Kallikratis administrative units

df = add_kapodistrias_adm(df, dfs['coord'])

#%% Save intermediate df

df.to_csv('../intermediate_databases/hellas_db_v1.1.csv')

#%% Load intermediate

df = pd.read_csv('../intermediate_databases/hellas_db_v1.1.csv', index_col = 'index')

#%% Prepare `edres` df

raw_census_filename = '../data/raw_data/raw_census.xls'
rcdf_raw = pd.read_excel(raw_census_filename)


# Get rid of first rows
rcdf = rcdf_raw[4:]

# Reaplce column names
rcdf.columns = ['level', 'nuts1', 'nut2', 'code', 'desc', 
              'iure11', 'facto11', 'iure01', 'facto01', 'iure91', 'facto91']

# Keep necessary rows and columns
rcdf = rcdf[rcdf['level'].between(2, 5)] # Only dimos (lvl. 5) and bigger units have capital
rcdf = rcdf.iloc[:, :5]
rcdf = rcdf[rcdf['desc'].str.contains('Έδρα: ')] # Retain rows with capital (apparently, Attiki does not have)

# Get `edra` columns
rcdf['edra'] = rcdf['desc'].apply(lambda x: x.split('Έδρα: ')[-1][:-1].split(', Ιστορική έδρα:')[0])

# Create `edres` df
edres = rcdf
edres.reset_index(inplace = True, drop = True)

# Create `full_code` column
edres['full_code'] = edres['nuts1'] + edres['nut2'] + edres['code']

#%% Add edres information

add_capital_data(df, edres)

#%% Save intermediate df

df.to_csv('../intermediate_databases/hellas_db_v1.2.csv')

#%% Load intermediate

df = pd.read_csv('../intermediate_databases/hellas_db_v1.2.csv', index_col = 'index')

#%% Add `island` column

add_island_status(df, island_adm)

#%% Save intermediate df

df.to_csv('../intermediate_databases/hellas_db_v1.3.csv')

#%% Load intermediate

df = pd.read_csv('../intermediate_databases/hellas_db_v1.3.csv', index_col = 'index')

#%% Save final df

df.to_csv(f'../final_databases/{filenames["full_database"]}.csv')
df.to_excel(f'../final_databases/{filenames["full_database"]}.xlsx')