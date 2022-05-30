# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

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
             'v1.0' : 'hellas_db_v1.0',
             'ELSTAT_census' : 'ELSTAT_census',
             'ELSTAT_urban' : 'ELSTAT_urban',
             'Geonames' : 'Geonames_processed',
             'ELSTAT_coord' : 'ELSTAT_coord',
             'Kal-Kap' : 'Kal-Kap_corresp'}

#%% Island variables

# Dictionary containing all units composed only by islands
island_adm = {'perif' : ['ΙΟΝΙΩΝ ΝΗΣΩΝ', 'ΒΟΡΕΙΟΥ ΑΙΓΑΙΟΥ', 'ΒΟΡΕΙΟΥ ΑΙΓΑΙΟΥ', 'ΚΡΗΤΗΣ'],
              'nomos' : ['ΘΑΣΟΥ', 'ΝΗΣΩΝ', 'ΣΠΟΡΑΔΩΝ'],
              'dimos' : ['ΣΑΜΟΘΡΑΚΗΣ'],
              'koinot' : ['Αμμουλιανής'],
              'original_name' : ['Τριζόνια,τα (νησίς)', 'Αιτωλικόν,το']}