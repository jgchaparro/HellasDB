# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

import pandas as pd
import numpy as np
import re
import requests

#%% Get Greek name

def get_greek_name(altname_lst):
    """Extracts the Greek name from the alternative names 
    column of the Geonames database"""
    try:
        return [an for an in altname_lst if an['lang'] == 'el'][0]['name']
    except:
        return np.nan

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
    
def dimotiki_simp(name):
    """Returns the dimotiki form for a name"""
    pass
    
    
def merge_census_gn(df, dfgn):
    """Checks if a town present in the census is contained
    in the Geonames database. If so, check if the specific town
    can be distinguished from homonymous towns in other provices and
    obtain its coordinates and elevation."""
    
    for i in range(0, len(df)):
        town = df.loc[i, 'desc']
        nomos = df.loc[i, 'nomos']
        print(f'Merging {town} ({nomos})')
        
        res = dfgn[dfgn['greek_name'].str.contains(town)]
    
        # If town name is unique, add results
        if len(res) == 1:
            print('Unique coincidence found!')
            add_info(res, df, i)
            continue
        
        # If not, filter by nomos
        elif len(res) > 1:
            res_filt = res[res['nomos'] == nomos]
            # If name is unique in the nomos, add results
            if len(res_filt) == 1:
                add_info(res_filt, df, i)
            


def add_info(res, df, i):
    """Adds coordinates and elevation to the main census df 
    based on a given index i"""
    
    search_cols = { # Column in census : column in geonames
                    'lat' : 'lat',
                    'long' : 'lng',
                    'elev' : 'elevation'}
    for cc, gc in search_cols.items(): # Census column, Geonames column
        df.loc[i, cc] = res[gc].iloc[0]    
        

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
