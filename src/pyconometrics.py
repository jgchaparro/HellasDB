# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 12:52:47 2020

@author: Usuario
"""

from sklearn.linear_model import LinearRegression
import numpy as np
import scipy.stats as stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd
import re

#%% Basic functions

def clean_df(dep_var, indep_var, raw_dataframe,
              par_log_dep_var = False, par_log_indep_var = [],
              squares = [], inters = []):
    '''Devuelve el df listo para realizar regresiones.'''
    
    # Quitar filas con NaN en la variable dependiente y NaN en independientes
    df = raw_dataframe[raw_dataframe[dep_var].notna()]
    
    all_vars = indep_var.copy()
    all_vars.insert(0, dep_var)
    
    # Añadir variable a independientes si solo aparece en las interacciones
    for iv_pair in inters:
        for inter_var in iv_pair:
            if inter_var not in all_vars:
                all_vars.append(inter_var)              
    
    df = df.loc[:, all_vars]
    df.dropna(inplace = True)
    df.reset_index(drop = True, inplace = True)
            
    # Crear columnas con log necesarias
    # Variables independientes
    for iv in par_log_indep_var:
        log_indep_var_name = 'l' + iv
        if log_indep_var_name not in indep_var:
            indep_var[indep_var.index(iv)] = log_indep_var_name
        if log_indep_var_name not in df.columns:
            df[log_indep_var_name] = np.log(df[iv])

    # Variables dependiente
    if par_log_dep_var:
        log_dep_var_name = 'l' + dep_var
        if log_dep_var_name not in df.columns:
            df[log_dep_var_name] = np.log(df[dep_var])
            
        
    # Crear variabels cuadráticas
    for sq_var in squares:
        sq_var_name = sq_var + '2'
        df[sq_var_name] = df[sq_var]**2
        indep_var.insert(indep_var.index(sq_var) + 1, sq_var_name)
    
    # Crear variables de interacción
    for inter in inters:
        inter_var_name = 'X'.join(inter)
        df[inter_var_name] = df[inter[0]] * df[inter[1]]
        indep_var.append(inter_var_name)
        
    new_df = df
    
    return new_df
    

def clean_reg(dep_var, indep_var, raw_dataframe,
              par_log_dep_var = False, par_log_indep_var = [],
              squares = [], inters = [], intercept = True,
              wls = False, weights = None):
    
    df = clean_df(dep_var, indep_var, raw_dataframe,
                  par_log_dep_var, par_log_indep_var,
                  squares, inters)
    
    if par_log_dep_var:
        dep_var = 'l' + dep_var

    y = df.loc[:, dep_var]
    X = df.loc[:, indep_var]
    
    if intercept:
        ones = pd.DataFrame(data = {'Intercept': [1] * len(X)})
        X = pd.concat([ones, X], axis = 1)
    
    regression = sm.OLS(y, X)
    if wls:
        regression = sm.WLS(y, X, weights = weights)
    results = regression.fit()
    return results         

#%% Auxiliary functions 
        
def f(*args):
    test_text = ', '.join([f'({var} = 0)' for var in args])
    return test_text

def lag(variables, raw_df, q = None):
    '''Lags n variables in `variables` by q periods.
    `q` should be a list of n ints specifying the number
    of periods to lag each variable. Otherwise, it is assumed
    that q = 1 for all variables.'''
    
    if isinstance(variables, str):
        variables = [variables]
   
    if q == None:
        q = [1] * len(variables)
    elif isinstance(q, int):
        q = [q]
         
    # Determinar si son datos de panel o series temporales comparando
    # la relación entre el set y los índices completos
    timeseries = len(set(raw_df.index)) == len(raw_df.index)
    
    for var, per in zip(variables, q):
        lagvar_name = lagname(var, q = per)
        if timeseries: # Series temporales
            raw_df[lagvar_name] = raw_df[var].shift(per)
        else:   # Datos de panel
            raw_df[lagvar_name] = raw_df[var].groupby(raw_df.index).shift(per)

def dif(raw_df, variables, log = None):
    '''Calculates the difference in variables.'''
    
    if log != None:
        for v, l in zip(variables, log):
            if l: # If log is True
                logvar_name = f'l{v}'
                raw_df[logvar_name] = np.log(raw_df[v])
                variables[variables.index(v)] = logvar_name
                
    lag(variables, raw_df)
    
    for var in variables:
        difvar_name = f'd{var}'
        raw_df[difvar_name] = raw_df[var] - raw_df[lagname(var)]        

def lagname(name, q = 1):
    lag_suf = re.findall(r'-\d+', name) # Finds -digit structure
    
    if len(lag_suf) == 0: # No lag
        lag_name = f'{name}-{q}'
    else: # Preexisting lag
        nl_name = name.split('-') # Variable name
        new_lag = str(int(nl_name[-1]) + q)
        lag_name = f'{nl_name[0]}-{new_lag}'
    
    return lag_name
        

def add_resid(reg, df, name = 'resid', 
              sq = False, sq_name = 'resid2',
              fill = np.nan):
    """Adds the residuals or the square residuals to the df."""
    
    resid = reg.resid
    
    if sq:
        resid = reg.resid ** 2
        name = sq_name
        
    df[name] = [np.nan] * (len(df) - len(resid)) + list(resid)
    

#%% Other regressions

def pred_reg(dep_var, indep_var, raw_dataframe, vals,
              par_log_dep_var = False, par_log_indep_var = [],
              squares = [], inters = [], intercept = True,
              wls = False, weights = None):
    
    mod_df = clean_df(dep_var, indep_var, raw_dataframe,
                  par_log_dep_var, par_log_indep_var,
                  squares, inters)
    
    reg_res = clean_reg(dep_var, indep_var, raw_dataframe,
                        par_log_dep_var, par_log_indep_var,
                        squares, inters, intercept,
                        wls, weights)

    pred_mean = reg_res.predict(vals)
    
    mod_vars = []
    
    # Puede que dé problemas con las interacciones, cuadrados y logaritmos
    # Se asume que habrá intercepto, tal vez haya que cambiarlo más adelante
    for iv, val in zip(indep_var, vals[0:]): 
        mod_var_name = f'{iv}_mod'
        mod_df[mod_var_name] = mod_df[iv] - val
        mod_vars.append(mod_var_name)
        
    mod_reg = clean_reg(dep_var, indep_var, mod_df,
              par_log_dep_var, par_log_indep_var,
              squares, inters, intercept,
              wls, weights)
    
    pred_std = mod_reg.bse['Intercept']
    pred_pvalue = mod_reg.pvalues['Intercept']
    
    pred_info = {'mean' : float(pred_mean),
                 'std' : pred_std,
                 'pvalue' : pred_pvalue,
                 '95 % CI': [float(pred_mean - 1.96 * pred_std), 
                             float(pred_mean + 1.96 * pred_std)]}
    
    return pred_info

def autocorr(df, var, q = 1):
    lag(var, df, q)
    
    #REGRESIÓN
    dep_var = var
    indep_var = [lagname(var)]
    
    reg = clean_reg(dep_var, indep_var, df,
                    intercept = False)
    
    autocorr_info = {'rho' : reg.params[lagname(var)],
                 'std' : reg.bse[lagname(var)],
                 'pvalue0' : reg.pvalues[lagname(var)],
                 'pvalue1': float(reg.t_test(f'{lagname(var)} = 1').pvalue)}
    
    return autocorr_info


def arsc(model, q = 1):
    
    df_dm = pd.DataFrame(data = {'resid' : model.resid})
    
    lag('resid', df_dm, q = q)
    
    ar_reg = clean_reg('resid', [f'resid-{q}'], df_dm,
                       intercept = False)

    return ar_reg

#%% FGLS regressions

def reg_fgls(dep_var, indep_var, raw_dataframe, 
             pw = False,
             par_log_dep_var = False, par_log_indep_var = [],
             squares = [], inters = [], intercept = True,
             wls = False, weights = None):
    """Estimates iteratively using feasible generalized least squares.
    By default, uses Cochrane-Orcutt estimation."""

    ols_reg = clean_reg(dep_var, indep_var, raw_dataframe,
              par_log_dep_var, par_log_indep_var,
              squares, inters , intercept,
              wls, weights)
    
    fgls_reg = OLSAR1(ols_reg, dep_var, indep_var, drop1 = not(pw))
    
    return fgls_reg

# cochrane-orcutt / prais-winsten with given AR(1) rho, 
# derived from ols model, default to cochrane-orcutt 
def ols_ar1(model,rho, dep_var, indep_var, drop1=True): 
    """Pass dep_var and indep_var for naming purposes"""
    
    x = model.model.exog
    y = model.model.endog
    ystar = y[1:]-rho*y[:-1]
    xstar = x[1:,]-rho*x[:-1,]
    if drop1 == False:
        ystar = np.append(np.sqrt(1-rho**2)*y[0],ystar)
        xstar = np.append([np.sqrt(1-rho**2)*x[0,]],xstar,axis=0)
    
    est_prefix = 'CO_'
    if not drop1:
        est_prefix = 'PW_'
    pref_indep_var = [f'{est_prefix}{v}' for v in ['Intercept'] + indep_var]
    
    ystar = pd.DataFrame(data = {f'{est_prefix}{dep_var}': ystar})
    xstar = pd.DataFrame(data = xstar, columns = pref_indep_var)
        
    model_ar1 = sm.OLS(ystar,xstar).fit()
    return(model_ar1)

# cochrane-orcutt / prais-winsten iterative procedure
# default to cochrane-orcutt (drop1=True)
def OLSAR1(model, dep_var, indep_var, drop1=True): 
    x = model.model.exog
    y = model.model.endog
    # Sacar residuos e
    e = y - (x @ model.params) # La segunda parte es y_pred
    e1 = e[:-1]; e0 = e[1:]
    rho0 = np.dot(e1,e[1:])/np.dot(e1,e1)
    rdiff = 1.0
    while(rdiff>1.0e-5):
        model1 = ols_ar1(model,rho0, dep_var, indep_var, drop1)
        e = y - (x @ model1.params)
        e1 = e[:-1]; e0 = e[1:]
        rho1 = np.dot(e1,e[1:])/np.dot(e1,e1)
        rdiff = np.sqrt((rho1-rho0)**2)
        rho0 = rho1
        print('Rho = ', rho0)
    # pint final iteration
    # print(sm.OLS(e0,e1).fit().summary())
    model1 = ols_ar1(model,rho0, dep_var, indep_var, drop1)
    return(model1)