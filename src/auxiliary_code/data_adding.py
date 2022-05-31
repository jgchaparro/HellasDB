# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

import time
   
#%% Adding Kapodristrias information

def add_kapodistrias_adm(df, dfc):
    """Adds the administrative units a town belonged to during the Kapodistrias
    plan by matching coordinates"""
    
    print('Adding Kapodistrias data')
    
    # Create temporary dfs
    return_df = df.copy()
    df_mod = df.copy()
    dfc_mod = dfc.copy()
    
    #df_mod = dfs['cp1']
    #dfc_mod = dfs['coord'].copy()
    
    #Remove NaNs in main df copy
    df_mod.dropna(inplace = True)
    
    # Remove problematic index
    prob_i = [2780, 4243, 5092, 5150, 5320, 8078, 9924]
    df_mod.drop(labels = prob_i, inplace = True)
       
    # Create `coordinates` columns
    df_mod['match_coord'] = [(x, y, z) for x, y, z in zip(df_mod['lat'], df_mod['long'], df_mod['h'])]
    dfc_mod['match_coord'] = [(x, y, float(z)) for x, y, z in zip(dfc_mod['lat'], dfc_mod['lon'], dfc_mod['h'])]
    
    # Convert to str
    df_mod['match_coord'] = df_mod['match_coord'].astype(str)
    dfc_mod['match_coord'] = dfc_mod['match_coord'].astype(str)
    
    # Select dfc columns
    dfc_mod2 = dfc_mod[['match_coord', 'diam', 'nomos', 'dimos', 'dimenot']]

    # Change index and column names
    dfc_mod2.columns = ['match_coord', 'diam_KAL', 'nomos_KAL', 'dimos_KAL', 'dimenot_KAL']
    
    # Columns to add to main df
    add_columns = ['diam_KAL', 'nomos_KAL', 'dimos_KAL', 'dimenot_KAL']
    
    # Join tables
    for i in df_mod.index:
        print(f'Adding index {i}')
        match_coord = df_mod.loc[i, 'match_coord']
        res = dfc_mod2[dfc_mod2['match_coord'] == match_coord]
        return_df.loc[i, add_columns] = res[add_columns].values[0]
            
    print('Kapodistrias data added!')
    
    df = return_df.copy()
    
    return df
    
#%% Add capital data

def add_capital_data(df, edres):
    """Marks the capital location of each administrative unit."""
    
    def apply_edra(i):
        # Get adm. unit code and edra
        code = lvl_df.loc[i, 'full_code'].strip()
        edra = lvl_df.loc[i, 'edra']
        # Filter by code
        lvl_locations = mod_df[mod_df['full_code'].str.startswith(code)]
        res = lvl_locations[lvl_locations['original_location_name'] == edra]
        
        # Add results to main df if there is only one coincidence
        if len(res) == 1:
            df.loc[res.index, col] = True
            
        elif len(res) == 0:
            # Use brute force for specific cases
            res = df[df['original_location_name'] == edra]
            if len(res) == 1:
                df.loc[res.index, col] = True
            else:
                res = df[df['original_location_name'].str.contains(edra)]
                if len(res) == 1:
                    df.loc[res.index, col] = True
                else:
                    print(f'Error witn index {i}')

        else: # More than one coincidence, take location with maximum population
            res.sort_values(by='facto11', ascending = False, inplace = True)
            index = res.iloc[0].name
            df.loc[index, col] = True
    
    # Create temporary dfs
    mod_df = df.copy()
    
    # Chage `code` column to string
    mod_df['full_code'] = mod_df['full_code'].astype(str)
    
    colnames = { # Adm. lvl : column name
                2 : 'edra_apok',
                3 : 'edra_perif',
                4 : 'edra_nomos',
                5 : 'edra_dimos'}
    
    for lvl, col in colnames.items():
        print(f'Merging level {lvl}')
        start = time.time()
        
        # Create column with False as default
        df[col] = False

        # Filter df by level
        lvl_df = edres[edres['level'] == lvl]
        
        # Apply `apply_edra` function
        list(map(apply_edra, lvl_df.index))
        
        print(f'Elapsed time: {time.time() - start}')
        
    

#%% Island data

def add_island_status(df, island_adm):
    """Adds true if the location is on an island.
    Euboia is excluded."""
    
    # Extract locations on islands
    island_df = df[(df['perifereia'].isin(island_adm['perif'])) | 
                    (df['nomos'].isin(island_adm['nomos'])) |
                    (df['dimos'].isin(island_adm['dimos'])) |
                    (df['original_location_name'].isin(island_adm['original_name']))]

    # Create `island` column
    df['island'] = False
    
    # Add island data based on index
    df.loc[island_df.index, 'island'] = True
        