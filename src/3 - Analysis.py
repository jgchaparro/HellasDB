import pandas as pd
import numpy as np

from utils import filenames
from pyconometrics import clean_reg

from sklearn.metrics import mean_squared_error as mse
from analysis_tools import corr

#%% Import data

df = pd.read_csv(f'../final_databases/{filenames["full_database"]}.csv')

bool_cols = ['astikotita', 'orinotita', 'island', 
             'edra_apok', 'edra_perif', 'edra_nomos', 'edra_dimos']
for col in bool_cols:
    df[col] = df[col].astype(int)


df2 = df[df['facto11'] < 500].dropna()
df2 = df[df['edra_dimos'] == 1].dropna()


#%% Regression

#REGRESIÓN
dep_var = 'facto11'
indep_var = [
            'facto01', 'facto91', 
            #'tcf1101', 
            'tcf0191',  
            #'pcf1101', 
            'pcf0191', 
             #'h', 
             #'astikotita', 
             #'orinotita',
             #'island',
             #'edra_nomos',
             'edra_perif'
             ]

reg1 = clean_reg(dep_var, indep_var, df2, 
                 intercept = False)
print(reg1.summary())

df2['const'] = 1
#indep_var.append('const')

y_pred = reg1.get_prediction(df2[indep_var]).predicted_mean
y_test = df2[dep_var]
rmse = mse(y_test, y_pred, squared=False)

#%% Correlations

corr(df2[indep_var])
