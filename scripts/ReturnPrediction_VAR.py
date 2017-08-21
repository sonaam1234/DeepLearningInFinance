# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 00:24:07 2017

@author: sonaa
"""
import os
import warnings
import numpy as np
import pandas as pd
#from keras.layers.core import Dense, Activation, Dropout
#from keras.layers.recurrent import LSTM
#from keras.models import Sequential
from datetime import datetime
import matplotlib.pyplot as plt
import statsmodels.tsa.api as sm
#from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.preprocessing import StandardScaler, Normalizer, MinMaxScaler
from statsmodels.tsa.arima_model import ARIMA

np.random.seed(7)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore") 

df = pd.read_hdf('DeepLearning.h5', 'Data_Gold')

for c in df.columns:
        df[c+'_ret'] = df[c].pct_change(2).fillna(0)
 
data = df.loc[:,['Gold_ret', 'DJI_ret', 'Inflation_ret']]  
var = sm.VAR(data)
#selecting VAR order
print (var.select_order(10))
results = var.fit(4)  
x_pred = results.fittedvalues 

df.loc[:, 'Pred_ret'] = x_pred.loc[:, 'Gold_ret']#arima.fittedvalues
df = df
df['Pred'] = df.Gold
for j in range(len(df.index)):
    if j < 4: 
        continue
    i = df.index[j]
    prev = df.index[j-2]
    df.loc[i, 'Pred'] = df.loc[prev, 'Pred']*(1 + df.loc[i, 'Pred_ret'])
df.to_hdf('DeepLearning.h5', 'Pred_VAR')
plt.plot(df['Gold'])
plt.plot(df['Pred'], label = 'pred')
plt.legend()
plt.show()