# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:32:13 2017

@author: sonaa
"""


import os
import time
import warnings
import numpy as np
import pandas as pd
from numpy import newaxis
from keras.layers.core import Dense, Activation, Dropout
from keras.layers import Convolution1D, MaxPooling1D, Flatten,  Embedding
from keras.layers import Conv1D, GlobalMaxPooling1D
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from datetime import datetime
import matplotlib.pyplot as plt
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
#val_df = train_df.loc[train_df.index >= pd.to_datetime('2013-01-01')]
#train_df = train_df.loc[train_df.index < pd.to_datetime('2013-01-01')]
#test_df = df.loc[df.index >= pd.to_datetime('2016-01-01')]
#train_x, train_y = create_dataset(train_df, look_back=look_back)
##val_x, val_y = create_dataset(val_df, look_back=look_back)
#test_x, test_y = create_dataset(test_df, look_back=look_back)

timeseries = np.asarray(df.Gold)
timeseries = np.atleast_2d(timeseries)
if timeseries.shape[0] == 1:
        timeseries = timeseries.T
X = np.atleast_3d(np.array([timeseries[start:start + look_back] for start in range(0, timeseries.shape[0] - look_back)]))
y = timeseries[look_back:]

predictors = ['Gold']#, 'DJI','Inflation']#, 'InterestRate']
#TRAIN_SIZE = train_x.shape[0]
#EMB_SIZE = look_back
model = Sequential()
#model.add(Embedding(TRAIN_SIZE, 1, input_length=EMB_SIZE))
model.add(Convolution1D(input_shape = (look_back,1), 
                        nb_filter=64,
                        filter_length=2,
                        border_mode='valid',
                        activation='relu',
                        subsample_length=1))
model.add(MaxPooling1D(pool_length=2))

model.add(Convolution1D(input_shape = (look_back,1), 
                        nb_filter=64,
                        filter_length=2,
                        border_mode='valid',
                        activation='relu',
                        subsample_length=1))
model.add(MaxPooling1D(pool_length=2))

model.add(Dropout(0.25))
model.add(Flatten())

model.add(Dense(250))
model.add(Dropout(0.25))
model.add(Activation('relu'))

model.add(Dense(1))
model.add(Activation('linear'))

start = time.time()
model.compile(loss="mse", optimizer="rmsprop")
model.fit(X, 
          y, 
          epochs=1000, 
          batch_size=80, verbose=1, shuffle=False)



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
        a = a
    y = model.predict(a.reshape(1,look_back*len(predictors),1))
    df.loc[df.index[i], 'Pred']=y[0][0]
df.to_hdf('DeepLearning.h5', 'Pred_CNN')
df.loc[:, 'Gold'] = sc.inverse_transform(df.loc[:, 'Gold'])
df.loc[:, 'Pred'] = sc.inverse_transform(df.loc[:, 'Pred'])
plt.plot(df.Gold,'y')
plt.plot(df.Pred, 'g')