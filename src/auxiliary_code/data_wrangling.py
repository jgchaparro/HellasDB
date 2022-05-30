# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

import pandas as pd
import numpy as np
import re
import requests as req
from auxiliary_code.utils import io_excepts
import time

#%% ELSTAT census functions

def unroll_census(df):
    """Converts the information about the administrative units a location
    belongs to to individual columns."""
    
    # Name of the new column, administrative level, census excel nomenclature
    for adm_name, lev, c_nom in [('region', 1, ''),
                             ('apok_dioikisi', 2, 'ΑΠΟΚΕΝΤΡΩΜΕΝΗ ΔΙΟΙΚΗΣΗ '),
                             ('perifereia', 3, 'ΠΕΡΙΦΕΡΕΙΑ '),
                             ('nomos', 4, 'ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ '), 
                             ('dimos', 5, 'ΔΗΜΟΣ '),
                             ('dimenot', 6, 'ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ '),
                             ('koinot', 7, 'Κοινότητα ')]:
        
        print(f'Unrolling level {lev}')
        
        # Create empty column with NaNs
        df[adm_name] = np.nan
        
        # Select desiderd indices
        indices = df.loc[df.level == lev].index
        
        # Use corresponding replace for each administrative level
        if lev == 1:
            for i in indices:
                df.loc[i, adm_name] = df.loc[i, 'location']
        
        elif 2 <= lev <= 5:
            for i in indices:
                df.loc[i, adm_name] = df.loc[i, 'location'].replace(c_nom, '').split(' (')[0]
        
        elif lev == 6:
            for i in indices:
                df.loc[i, adm_name] = df.loc[i, 'location'].split(c_nom)[-1]
        else: # if lev == 7:
            for i in indices:
                df.loc[i, adm_name] = df.loc[i, 'location'].split(c_nom)[-1]
                df.loc[i, 'koinot_id'] = df.loc[i, 'code']
    
    # Apply forward fill
    df.ffill(inplace = True)

#%% Conversion to dimotiki functions

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

#%% Functions to extract article

def extract_article(location):
    """Extracts the artcle of a location name following the pattern
    'name,article'. Returns a NaN if the pattern is not found."""
    
    try:
        # Split to get article after comma, then
        # split to remove "nisis" information, then
        # split to remove certain locations with ' - ' in the name
        art = location.split(',')[1].split(' (')[0].split(' - ')[0]
        
    except:
        art = np.nan
    
    return art
    