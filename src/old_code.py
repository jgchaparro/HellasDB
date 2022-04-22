# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

import pandas as pd
import numpy as np
import re
import requests as req
from joblib import Parallel, delayed
from utils import io_excepts

#%% Geonames database functions

def retrieve_API_info(raw_gn_csv_path):
    """Extracts information about Greek towns from Geonames API."""
    
    base_url = 'http://api.geonames.org/searchJSON?'

    # Get all perifereies
    reg_gn = req.get(base_url, params = {
                                        'formatted' : 'true',
                                        'country' : 'GR',
                                        'fcode' : 'adm1',
                                        'username' : 'jgchaparro',
                                        'style' : 'full'}).json()['geonames']

    # Get region bboxes. Exclude Mount Athos: not present in census.
    reg_bbox = {r['name'] : r['bbox'] for r in reg_gn if r['name'] != 'Mount Athos'}

    # ----------------------------------------

    # Get towns for each region
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
        
        #towns = {r['name'] : r for r in reg_json} - Apparently unused
        reg_df = pd.json_normalize(reg_json)
        rdfs[k] = reg_df

    # ------------------------------------------

    # Join all dfs and first steps cleaning Geonames df
    dfgn = pd.concat([d for d in rdfs.values()]).reset_index().drop(columns = ['index'])

    # Save dfgn to avoid retrieving data
    # Change alternateName column to Greek to avoid losing data
    dfgn['greek_name'] = [dimotiki_simp(get_greek_name(x)) for x in dfgn.alternateNames]
    dfgn.drop(columns = 'alternateNames', inplace = True)

    # Save raw df
    dfgn.to_csv(raw_gn_csv_path, index = False)
    print(f'Geonames dataframe saved in {raw_gn_csv_path}')
    
    return dfgn

#%% Merging functions

def merge_census_gn(df, dfgn):
    """Checks if a town present in the census is contained
    in the Geonames database. If so, check if the specific town
    can be distinguished from homonymous towns in other provices and
    obtain its coordinates and elevation."""
    
    def filter_town(i):
        town = df.loc[i, 'desc']
        nomos = df.loc[i, 'nomos']
        print(f'Merging {town} ({nomos})')
        
        res = dfgn[dfgn['greek_name'].str.contains(town)]
    
        # If town name is unique, add results
        if len(res) == 1:
            #print('Unique coincidence found!')
            add_info(res, df, i)
        
        # If not, filter by nomos
        elif len(res) > 1:
            res_filt = res[res['nomos'] == nomos]
            #print(res_filt)
            # If name is unique in the nomos, add results
            if len(res_filt) == 1:
                add_info(res_filt, df, i)
                #print('Unique coincidence found!')
    
    def add_info(res, df, i):
        """Adds coordinates and elevation to the main census df 
        based on a given index i"""
        
        search_cols = { # Column in census : column in geonames
                        'lat' : 'lat',
                        'long' : 'lng',
                        #'elev' : 'elevation' # Not enough elements
                        }
        for cc, gc in search_cols.items(): # Census column, Geonames column
            df.loc[i, cc] = res[gc].iloc[0]    
            
    #Create empty columns to be populated later
    new_cols = ['lat', 'long']
    for col in new_cols:
        df[col] = np.nan
    
    # Use paralellization to join
    # Parallel(n_jobs=6, verbose=True)(delayed(filter_town)(i) for i in range(len(df)))
    
    # Use map to merge
    list(map(filter_town, range(len(df))))
    
    #for i in range(len(df)):
    #    filter_town(i)