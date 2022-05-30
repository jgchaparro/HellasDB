#%% 

import pandas as pd
import pylab as plt
import numpy as np
import seaborn as sns

from scipy.stats import spearmanr, pearsonr

from sklearn.linear_model import LinearRegression as LinReg
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.linear_model import ElasticNet
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor as RFR
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import ExtraTreeRegressor as ETR
from sklearn.ensemble import GradientBoostingRegressor as GBR
from xgboost import XGBRegressor as XGBR
from catboost import CatBoostRegressor as CTR
from lightgbm import LGBMRegressor as LGBMR

from sklearn.metrics import mean_squared_error as mse
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA

import statsmodels.api as sm
import pickle


#%% Evaluate

def corr(X):
    corr = X.corr()

    fig, ax=plt.subplots(figsize=(10,10))
    mask=np.triu(np.ones_like(corr, dtype=bool))
    color_map=sns.diverging_palette(0, 10, as_cmap=True)

    # correlation heatmap
    sns.heatmap(corr,                       
                mask=mask,                  
                cmap=color_map,             
                vmax=1,                     
                center=0,                   
                square=True,                
                linewidth=.5,               
                cbar_kws={'shrink': .5},    
                ax=ax,                       
                annot = True);

#%% Initialize models

def initialize_models(min_n_estimators = 10, max_n_estimators = 100,
                      n_estimators = 20,
                      learning_rates = [0.3, 0.1, 0.03]):
    linreg=LinReg()
    lasso=Lasso()
    ridge=Ridge()
    elastic=ElasticNet()

    svr=SVR()

    rfr=RFR(n_estimators = 50)
    etr=ETR()

    #gbr=GBR()
    ctr=CTR()
    
    models = [linreg, lasso, ridge, elastic, svr, etr]
    
    # Initialize XGB and LGBM with several n. of trees
    trees_mod = [GBR, XGBR, LGBMR]
    n_estimators = np.linspace(min_n_estimators, 
                               max_n_estimators, 
                               n_estimators)
    for model in trees_mod:
        for n in n_estimators:
            for lr in learning_rates:
                models.append(model(n_estimators = int(n), 
                                    learning_rate = lr))
        
    return models

#%% Train all models

def get_best(models, X_train, X_test, y_train, y_test):
    """Selects the best model from a list of models"""
    
    # Initialize counter for RMSE
    min_rmse = 1e6
    best_model = None
    
    for i, m in enumerate(models):
        m.fit(X_train, y_train)
        y_pred = m.predict(X_test)

        rmse = mse(y_test, y_pred, squared=False)
        #print(m)
        #print(f'{i} = {rmse}')
        if rmse < min_rmse:
            min_rmse = rmse
            best_model_i = i
        
        
    best_model = models[best_model_i]
    # Create dictionary with information about the best model
    best_model_dic = {'model' : best_model, 
                      'rmse' : min_rmse,
                      'params' : X_train.columns.tolist()}
    
    if hasattr(best_model, 'learning_rate'):
        best_model_dic['learning_rate'] = best_model.learning_rate
    
    return best_model_dic
 
#%% Get lineal and non-lineal correlations

def non_linear_test(y, X):
    """Checks if there are non linear correlations.
    If the difference of the columns is big, 
    there must be non-linear correlation."""
    
    corr_df = pd.DataFrame(data = None)
    
    for col in X.columns:
        
        corr_df.loc[col, 'L'] = pearsonr(y, X[col])[0]
        corr_df.loc[col, 'NL'] = spearmanr(y, X[col])[0]
        corr_df.loc[col, 'dif'] = corr_df.loc[col, 'NL'] - corr_df.loc[col, 'L']
    
    # Generate plot    
    
    fig, ax=plt.subplots(figsize=(10,10))
    color_map=sns.diverging_palette(0, 10, as_cmap=True)

    # correlation heatmap
    sns.heatmap(corr_df,                       
                cmap=color_map,             
                vmax=1,                     
                center=0,                   
                square=True,                
                linewidth=.5,               
                cbar_kws={'shrink': .5},    
                ax=ax,                       
                annot = True)
    
    plt.title('Linear and nonlinear correlations');


#%% Clean for analysis

def preprocess(X, y = None,
            drop_cols = [],
            log_y = False, log_x = [],
            squares = [], inters = [], 
            intercept = True, normalized = False):
    """Cleans the dataframe for analysis."""

    def preprocess_y(y, log_y = False):
        """Preprocesses dependent variable."""
        
        # Variables dependiente
        if log_y:
            y = np.log(y)
        
        return y

    X_ = X.copy()
    
    # Drop columns
    if drop_cols != []:
        X_ = X_.drop(drop_cols, axis=1)

    # Crear columnas con log necesarias
    # Variables independientes
    for x in log_x:
        log_x_name = 'l' + x
        if log_x_name not in X.columns:
            X_[log_x_name] = np.log(X_[x])
            X_.drop(x, axis = 1, inplace = True)

            
    # Crear variables cuadráticas
    for sq_var in squares:
        sq_var_name = sq_var + '2'
        X_[sq_var_name] = X_[sq_var]**2
    
    # Crear variables de interacción
    for inter in inters:
        inter_var_name = 'X'.join(inter)
        X_[inter_var_name] = X_[inter[0]] * X_[inter[1]]
        
    if intercept:
        X_ = sm.add_constant(X_)
        
    if normalized:
        norm_col_names = ['norm_' + col for col in X_.columns]
        X_ = pd.DataFrame(data = PCA().fit_transform(X_), 
                          columns = norm_col_names, 
                          index = X_.index)
    
    # Procesar variable dependiente
    if y is not None:
        y_ = y.copy()
        y_ = preprocess_y(y_, log_y)
        return X_, y_
    
    else:
        return X_

#%% OLS test

def ols_analysis(y, X,
                 wls = False, weights = None):
    """Performs an exploratory OLS regression.
        
    --- IMPORT STATMODELS FIRST----
    import statsmodels.api as sm""" 
        
    # Perform regression
    regression = sm.OLS(y, X)
    results = regression.fit()
    f_score = results.fvalue
    r2_adj = results.rsquared_adj
    
    # Print results
    print(results.summary())
    print(f'F-Score = {f_score}')
    print(f'R2 adj. = {r2_adj}')
    
    
    return r2_adj

#%% Importance of features based on RFR regression

def rfr_analysis(y, X,
                 min_n_estimators = 50, max_n_estimators = 1000,
                 n_estimators = 20):
    """Analyses the importance of features based on a random forest regression.
    Splits the sample and takes the importance of the model with the minimum
    test error."""
    
    
    # Determine number of estimators
    n_estimators = np.linspace(min_n_estimators, max_n_estimators, n_estimators)
    n_estimators = n_estimators.astype(int)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    
    # Initialize control variables
    best_rfr = None    
    best_n_est = 0
    min_rmse = 1e6
    
    
    # Train models
    for n_est in n_estimators:
        #print(f'Estimating with {n_est} estimators')
        rfr = RandomForestRegressor(n_est)
        rfr.fit(X_train, y_train)
        y_pred = rfr.predict(X_test)

        rmse = mse(y_test, y_pred, squared=False)
        if rmse < min_rmse:
            min_rmse = rmse
            best_n_est = n_est
            best_rfr = rfr
    
    # Show preliminary results
    print(f'Optimal estimators: {best_n_est}')
    print(f'RMSE: {min_rmse}')
    
    # Get features importance
    imp_data = best_rfr.feature_importances_
    indices = X.columns
    
    # Build series
    imp_series = pd.Series(imp_data, indices)
    imp_series.sort_values(ascending = False, inplace = True)
    
    # Generate graph
    ax = sns.barplot(x = np.round(imp_series.values * 100, 2), y = imp_series.index)
    ax.bar_label(ax.containers[0])
    plt.title('Relative importance of independent variables')
    plt.xlabel('Relative importance (%)');
    
        
#%% PCA analysis

def pca_analysis(X):
    """Graphs the variance explined after performing PCA"""
    
    pca = PCA()
    
    pca.fit(X)
    pca.explained_variance_ratio_
    
    # Plot explained variance ratio
    plt.figure(figsize=(10, 5))

    plt.plot(np.cumsum(pca.explained_variance_ratio_))
    
    plt.xlabel('N. of components ')
    plt.ylabel('% variance')
    plt.ylim([0, 1.01]);
    
def apply_pca(X, n):
    
    pca = PCA(n_components = n)

    X_mod = pd.DataFrame(pca.fit_transform(X), 
                         columns = [f'PCA_{i}' for i in range(n)])
    
    return X_mod

#%% Get predictions for y when log_y is the dependent variable

def ols_predict_log_y(y, X, X_to_predict):
    
    log_y = np.log(y)
    
    regression = sm.OLS(log_y, X)
    results = regression.fit()
    
    # Compute alpha
    n = len(X)
    resid = results.resid
    exp_resid = np.sum(np.exp(resid))
    alpha = exp_resid/n
    
    # Predict
    log_y_pred = results.get_prediction(X_to_predict).predicted_mean
    y_pred = alpha * np.exp(log_y_pred)
    
    return y_pred