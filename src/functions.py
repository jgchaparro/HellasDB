# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

import pandas as pd
import numpy as np
import re
import requests as req

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
    
    # Use map to merge
    list(map(filter_town, range(len(df))))
    
    #for i in range(len(df)):
    #    filter_town(i)

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

#%% Transliterate nomos names

# Taken from sorted(dfgn['adminName2'].value_counts().index.tolist())
# Nomos Greek names taken from sorted(df.nomos.unique())
# Key = Geonames names
# Value = Census names

translits = {
             'Achaea' : 'ΑΧΑΪΑΣ',
             'Aitoloakarnania' : 'ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ',
             'Arcadia' : 'ΑΡΚΑΔΙΑΣ',
             'Argolís' : 'ΑΡΓΟΛΙΔΑΣ',
             'Chalkidikí' : 'ΧΑΛΚΙΔΙΚΗΣ',
             'Chania' : 'ΧΑΝΙΩΝ',
             'Chios' : 'ΧΙΟΥ',
             'Corinthia' : 'ΚΟΡΙΝΘΙΑΣ',
             'Dráma' : 'ΔΡΑΜΑΣ',
             'Euboea' : 'ΕΥΒΟΙΑΣ',
             'Evros' : 'ΕΒΡΟΥ',
             'Evrytanía' : 'ΕΥΡΥΤΑΝΙΑΣ',
             'Florina' : 'ΦΛΩΡΙΝΑΣ',
             'Grevena' : 'ΓΡΕΒΕΝΩΝ',
             'Heraklion' : 'ΗΡΑΚΛΕΙΟΥ',
             'Ilia Prefecture' : 'ΗΛΕΙΑΣ',
             'Imathia' : 'ΗΜΑΘΙΑΣ',
             'Ioannina' : 'ΙΩΑΝΝΙΝΩΝ',
             'Kardítsa' : 'ΚΑΡΔΙΤΣΑΣ',
             'Kastoria' : 'ΚΑΣΤΟΡΙΑΣ',
             'Kavala' : 'ΚΑΒΑΛΑΣ',
             'Kefallonia' : 'ΚΕΦΑΛΛΗΝΙΑΣ',
             'Kilkís' : 'ΚΙΛΚΙΣ',
             'Kozani' : 'ΚΟΖΑΝΗΣ',
             'Kérkyra'  : 'ΚΕΡΚΥΡΑΣ',
             'Laconia'  : 'ΛΑΚΩΝΙΑΣ',
             'Lasithi' : 'ΛΑΣΙΘΙΟΥ',
             'Lefkada' : 'ΛΕΥΚΑΔΑΣ',
             'Lesbos' : 'ΛΕΣΒΟΥ',
             'Lárisa' : 'ΛΑΡΙΣΑΣ',
             'Magnesia' : 'ΜΑΓΝΗΣΙΑΣ',
             'Messenia' : 'ΜΕΣΣΗΝΙΑΣ',
             'Nomós Piraiós' : 'ΠΕΙΡΑΙΩΣ',
             'Pella' : 'ΠΕΛΛΑΣ',
             'Phocis' : 'ΦΘΙΩΤΙΔΑΣ',
             'Phthiotis' : 'ΦΘΙΩΤΙΔΑΣ',
             'Pieria' : 'ΠΙΕΡΙΑΣ',
             'Préveza' : 'ΠΡΕΒΕΖΑΣ',
             'Rethymno' : 'ΡΕΘΥΜΝΟΥ',
             'Rodópi' : 'ΡΟΔΟΠΗΣ',
             'Samos' : 'ΣΑΜΟΥ',
             'Sérres' : 'ΣΕΡΡΩΝ',
             'Thesprotia' : 'ΘΕΣΠΡΟΤΙΑΣ',
             'Thessaloniki' : 'ΘΕΣΣΑΛΟΝΙΚΗΣ',
             'Trikala' : 'ΤΡΙΚΑΛΩΝ',
             'Voiotía' : 'ΒΟΙΩΤΙΑΣ',
             'Xanthi' : 'ΞΑΝΘΗΣ',
             'Zákynthos' : 'ΖΑΚΥΝΘΟΥ',
             'Árta' : 'ΑΡΤΑΣ',
             
             # No one to one relatonship between census and Geonames
             # Added custom nomoi to complete the list
             'Attica' : 'ΑΤΤΙΚΗΣ', 
             'Kykládes'  : 'ΚΥΚΛΑΔΩΝ',
             'Dodecanese' : 'ΔΩΔΕΚΑΝΗΣΩΝ',
             'Nomarchía Anatolikís Attikís' : 'ΑΤΤΙΚΗΣ',
             'Nomarchía Athínas' : 'ΑΘΗΝΩΝ'
             }


#%% Other variables

# Town names ending in -io in dimotiki
io_excepts = {'Λαύριον' : 'Λαύριο',
             'Νυδρίον' : 'Νυδρί'}

# MySQL pass_
with open('../data/MySQL_pass.txt') as f:
    pass_ = f.read()

# Files names
filenames = {'full_database' : 'hellas_db',
             'ELSTAT_census' : 'ELSTAT_census',
             'ELSTAT_urban' : 'ELSTAT_urban',
             'Geonames' : 'Geonames_processed'}