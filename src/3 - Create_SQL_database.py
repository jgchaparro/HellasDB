# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 10:43:24 2022

@author: Jaime García Chaparr
"""

#%% Import modules

import mysql.connector as conn
import pymysql
from sqlalchemy import create_engine
import pandas as pd

from utils import pass_, filenames

#%% Import database

db = pd.read_csv(f'../final_databases/{filenames["full_database"]}.csv')

#%% Create MySQL connection string

mysql_str_conn = f'mysql+pymysql://jgchaparro:{pass_}@127.0.0.1:3306/'
mysql_motor = create_engine(mysql_str_conn)

#%% Reinitialize DB

db_name = 'Hellas_DB'

try:
    mysql_motor.execute(f'DROP DATABASE {db_name};')
except:
    pass
mysql_motor.execute(f'CREATE DATABASE {db_name};')

str_conn = f'mysql+pymysql://jgchaparro:{pass_}@127.0.0.1:3306/{db_name}'
motor = create_engine(str_conn)

#%% Export to MySQL

db.to_sql(name = 'main', con = motor, if_exists = 'replace', index = True)
print(f'{db_name} created')