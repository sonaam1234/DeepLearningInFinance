# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 00:24:07 2017

@author: sonaa
"""
import os
import warnings
import numpy as np
import pandas as pd
from arch import arch_model
#from keras.layers.core import Dense, Activation, Dropout
#from keras.layers.recurrent import LSTM
#from keras.models import Sequential
from datetime import datetime
import matplotlib.pyplot as plt
#from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.preprocessing import StandardScaler, Normalizer, MinMaxScaler
from statsmodels.tsa.arima_model import ARIMA

np.random.seed(7)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore") 

d_f = pd.read_hdf('DeepLearning.h5', 'Data_Gold')

for c in d_f.columns:
        d_f[c+'_ret'] = d_f[c].pct_change(2).fillna(0)
        
    
sc = StandardScaler()
#d_f['Gold_ret'] = sc.fit_transform(d_f['Gold_ret'])
#402
#113
#302
step = 30
for ai in range(0, len(d_f), step):
    df = d_f.loc[d_f.index[ai:ai+step], :]
    x = df['Gold_ret']
    x_min = min(x)
    x_max = max(x)
#    x = (x - x_min)/(x_max-x_min)
#    sc = StandardScaler()
#    x = sc.fit_transform(x)
    ##based on model AIC
    min_aic = np.inf
    best_params = (1,1,1)
    for i in range(1,6):
        for j in range(6):
            for k in range(1,6):
                model = arch_model(x, mean = 'ARX', vol= 'Garch', p=i, o=j, q=k).fit(disp='off')
                if model.aic < min_aic:
                    min_aic = model.aic
                    best_params = (i,j,k)
    print ('Params of GARCH model', best_params) #(1,1,1)
    model = arch_model(x, mean = 'ARX', vol= 'Garch', p=best_params[0], o=best_params[1], q=best_params[2]).fit(disp='off')
#    print ('AIC of ARIMA model', arima.aic)
#    print ('Params of ARIMA model', best_params)
    
#    x_pred = arima.fittedvalues
#    x_pred = x_pred*(x_max - x_min) + x_min
#    d_f.loc[df.index, 'Gold_pred_ret'] = x_pred#arima.fittedvalues
#df = d_f
#df['Gold_pred'] = df.Gold
#for j in range(len(df.index)):
#    if j < 2: 
#        continue
#    i = df.index[j]
#    prev = df.index[j-2]
#    df.loc[i, 'Gold_pred'] = df.loc[prev, 'Gold_pred']*(1 + df.loc[i, 'Gold_pred_ret'])
#plt.plot(df['Gold'])
#plt.plot(df['Gold_pred'], label = 'pred')
#plt.legend()
#plt.show()