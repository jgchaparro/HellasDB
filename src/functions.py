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

#%% ELSTAT census functions

def unroll_census(df):
    
  
    for adm_name, lev, c_nom in [('perifereia', 3, 'ΠΕΡΙΦΕΡΕΙΑ '),
                                 ('nomos', 4, 'ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ '), 
                                 ('dimos', 5, 'ΔΗΜΟΣ '),
                                 ('dimenot', 6, 'ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ '),
                                 ('koinot', 7, 'Κοινότητα ')]:
        
        print(f'Unrolling level {lev}')
        df[adm_name] = np.nan
        indices = df.loc[df.level == lev].index
        for i in indices:
            if lev < 6:
                df.loc[i, adm_name] = df.loc[i, 'desc'].replace(c_nom, '').split(' (')[0]
            elif lev >= 6:
                df.loc[i, adm_name] = df.loc[i, 'desc'].split(c_nom)[-1]
                if lev == 7:
                    df.loc[i, 'koinot_id'] = df.loc[i, 'code']
    
    # Forward fill
    df.ffill(inplace = True)


def dimotiki(name):
    """Translates names in katharevousa to dimotiki and
    extracts the article."""
    
    #TODO drymon - drymonas
    
    try:
        data = {}
        
        data['kath'] = name.split(',')[0]
        data['dim'] = data['kath']
        
        data['article_kath'] = name.split(',')[-1]
        data['article_dim'] = data['article_kath']
        
        
        # Replace 'ις'
        data['dim'] = data['kath'].replace('ις', 'ιδα').replace('ίς', 'ίδα')
        
        # If neuter singular
        if data['article_kath'] == 'το':
            mod_name = data['kath'] + ' '
            data['dim'] = re.sub('([οό])ν', r'\1', mod_name).strip()
            
            # If ended in -io, most names in dimotiki end in -i,
            # but with exceptions. Exceptions tend to be preceded by
            # vowels. Even at this point, there are exceptions: Lavrio
            global io_excepts
            if re.search('[^αάεέ][ιί][οό]$', data['dim']) is not None and \
                data['dim'] not in io_excepts:
                data['dim'] = re.sub('[οό]$', '', data['dim'])
            elif data['kath'] in io_excepts.keys():
                data['dim'] = io_excepts[data['kath']]
            
            # Correct 'Χωρί' for 'Χωριό'
            if 'Χωρί' in data['dim']:
                data['dim'] = re.sub('Χωρί$', 'Χωριό', data['dim'])
            
            return data
                
        # If masculine plural
        elif data['article_kath'] == 'οι':
            name = data['kath']
            if name[-2:] == 'αι':
                data['dim'] = name[:-2] + 'ες'
                return data
            elif name[-2:] == 'αί':
                data['dim'] = name[:-2] + 'ές' 
                return data
            else:
                return data
            
        # If femenine plural
        elif data['article_kath'] == 'αι':
            name  = data['kath']
            data['article_dim'] = 'οι'
            if name[-2:] == 'αι':
                data['dim'] = name[:-2] + 'ες'
                return data
            elif name[-2:] == 'αί':
                data['dim'] = name[:-2] + 'ές' 
                return data
            else:
                return data
        else:
            return data
        
    except:
        return {'kath' : name, 
                'dim' : name,
                'article_kath' : np.nan,
                'article_dim' : np.nan}




def get_greek_name(altname_lst):
    """Extracts the Greek name from the alternative names 
    column of the Geonames database"""
    try:
        return [an for an in altname_lst if an['lang'] == 'el'][0]['name']
    except:
        return np.nan

    
def dimotiki_simp(name):
    """Returns the dimotiki form for a name"""
    
    try:
        if re.search('([οό])ν$', name) is not None:
            name = re.sub('([οό])ν ', r'\1 ', name + ' ').strip()
            
            global io_excepts
            if re.search('[^αάεέ][ιί][οό]$', name) is not None and \
                name not in io_excepts:
                name = re.sub('[οό]$', '', name)
            elif name in io_excepts.keys():
                name = io_excepts[name]
        
        elif name[-2:] == 'αι':
            name = name[:-2] + 'ες'
        elif name[-2:] == 'αί':
            name = name[:-2] + 'ές' 
                    
        return name
    except:
        return name
    
#%% Merging functions

def merge_census_urban(df, dfu):
    """Adds terrain information from ELSTAT urban table to
    the main dataframe based on the full code of the town
    (NUT1 + NUTS2 + code)."""
    
    #Create empty columns to be populated later
    new_cols = ['astikotita', 'orinotita']
    for col in new_cols:
        df[col] = np.nan
    
    # Add information
    for i in df.index:
        try:
            code = df.loc[i, 'koinot_id']
            for col in new_cols:
                df.loc[i, col] = dfu.loc[code, col]
        except:
            print(f'Invalid code: i = {i}')

    # Correct datatype
    df['astikotita'] = df['astikotita'].astype(bool)

def merge_census_coord(df, dfc):
    
    def filter_town(i):
        town = df.loc[i, 'original_name']
        nomos = df.loc[i, 'nomos']
        nomos_dimos = df.loc[i, 'nomos-dimos']
        print(f'Merging {town} ({nomos})')
        
        res = dfc[dfc['full_name'] == town]
    
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
            
            # If not, filter by dimos-nomos combination
            else:
                res_filt2 = res[res['nomos-dimos'] == nomos_dimos]
                if len(res_filt2) == 1:
                    add_info(res_filt, df, i)
                
    
    def add_info(res, df, i):
        """Adds coordinates and elevation to the main census df 
        based on a given index i"""
        
        search_cols = { # Column in census : column in geonames
                        'lat' : 'lat',
                        'long' : 'lon',
                        'h': 'h' # Not enough elements
                        }
        for cc, gc in search_cols.items(): # Census column, Geonames column
            df.loc[i, cc] = res[gc].iloc[0]    
            
    #Create empty columns to be populated later
    new_cols = ['lat', 'long', 'h']
    for col in new_cols:
        df[col] = np.nan
    
    list(map(filter_town, range(len(df))))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    