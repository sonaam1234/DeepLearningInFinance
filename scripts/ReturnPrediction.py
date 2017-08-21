# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:32:13 2017

@author: sonaa
"""


import os
import warnings
import numpy as np
import pandas as pd
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from datetime import datetime
import matplotlib.pyplot as plt
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.preprocessing import StandardScaler, Normalizer

np.random.seed(7)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore") 

df = pd.read_hdf('DeepLearning.h5', 'Data_Gold')


for c in df.columns:
    df[c+'_ret'] = df[c].pct_change().fillna(0)

def create_dataset(dataset, look_back=1, columns = ['Gold']):
    dataX, dataY = [], []
    for i in range(len(dataset.index)):
        if i <= look_back:
            continue
        a = None
        for c in columns:
            b = dataset.loc[dataset.index[i-look_back:i], c].as_matrix()
            if a is None:
                a = b
            else:
                a = np.append(a,b)
        dataX.append(a)
        dataY.append(dataset.loc[dataset.index[i], columns].as_matrix())
    return np.array(dataX), np.array(dataY)

look_back = 12
sc = StandardScaler()
df.loc[:, 'Gold'] = sc.fit_transform(df.loc[:, 'Gold'])
sc1 = StandardScaler()
df.loc[:, 'Inflation'] = sc1.fit_transform(df.loc[:, 'Inflation'])
sc2 = StandardScaler()
df.loc[:, 'InterestRate'] = sc1.fit_transform(df.loc[:, 'InterestRate'])
sc2 = StandardScaler()
df.loc[:, 'DJI'] = sc1.fit_transform(df.loc[:, 'DJI'])

train_df = df.loc[df.index < pd.to_datetime('2016-01-01')]
val_df = train_df.loc[train_df.index >= pd.to_datetime('2013-01-01')]
train_df = train_df.loc[train_df.index < pd.to_datetime('2013-01-01')]
test_df = df.loc[df.index >= pd.to_datetime('2016-01-01')]

predictors = ['Gold', 'DJI','Inflation']#, 'InterestRate']
train_x, train_y = create_dataset(train_df, look_back=look_back, columns = predictors)
val_x, val_y = create_dataset(val_df, look_back=look_back, columns = predictors)
test_x, test_y = create_dataset(test_df, look_back=look_back, columns = predictors)

model = Sequential()
model.add(Dense(10, activation='tanh', kernel_initializer='normal',
                input_dim=look_back*len(predictors)))
model.add(Dropout(0.2))
model.add(Dense(5, activation='tanh',kernel_initializer='normal'))
model.add(Dropout(0.2))
model.add(Dense(len(predictors)))

model.compile(loss="mse", optimizer="adam")
model.fit(train_x, 
          train_y, epochs=10000, 
          batch_size=50, verbose=2,shuffle=False, validation_data= (val_x, val_y))

df['Pred'] = df.loc[df.index[0], 'Gold']
for i in range(len(df.index)):
    if i <= look_back:
        continue
    a = None
    for c in predictors:
        b = df.loc[df.index[i-look_back:i], c].as_matrix()
        if a is None:
            a = b
        else:
            a = np.append(a,b)
    y = model.predict(a.reshape(1,look_back*len(predictors)))
    df.loc[df.index[i], 'Pred']=y[0][0]
    
df.loc[:, 'Gold'] = sc.inverse_transform(df.loc[:, 'Gold'])
df.loc[:, 'Pred'] = sc.inverse_transform(df.loc[:, 'Pred'])
df.to_hdf('DeepLearning.h5', 'Pred_DeepRegression')
plt.plot(df.Gold,'y')
plt.plot(df.Pred, 'g')

