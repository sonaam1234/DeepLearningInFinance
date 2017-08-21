# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 15:10:04 2017

@author: 44010195
"""
import pandas as pd
import numpy as np
#import pandas.io.data as web
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from sklearn.preprocessing import Normalizer, StandardScaler
import matplotlib.pyplot as plt

df = pd.read_csv('dji.csv', index_col = 'Date')
df.index = pd.to_datetime(df.index)
df = df.resample('W-MON', how = 'last')
stox = list(df.columns)
stox.remove('^DJI')
ind = '^DJI'
df = df[df.index > pd.to_datetime('1-1-2010')]
df = df[df.index < pd.to_datetime('17-4-2014')]

df['ret'] = df['^DJI'].pct_change().fillna(0.1)
df.loc[:, 'new_ret'] = df.apply(lambda r: 0.1 if r['ret'] < -0.08 else r['ret'], axis = 1)
df['new_index'] = df.loc[df.index[0], '^DJI']

for i in range(len(df.index)):
    if i > 0:
#        print (1.0-df.loc[df.index[i], 'new_ret'], df.loc[df.index[i-1], 'new_index'])
        df.loc[df.index[i], 'new_index'] = df.loc[df.index[i-1], 'new_index']*(1.0+df.loc[df.index[i], 'new_ret'])
        
en = StandardScaler()
df['^DJI'] = en.fit_transform(df['^DJI'])

for s in stox:
    en1 = StandardScaler()
    df[s] = en1.fit_transform(df[s])
    
df['new_index'] = en.transform(df['new_index'])

train = df[df.index < pd.to_datetime('17-04-2014')]
test = df[(df.index >= pd.to_datetime('17-4-2013')) & (df.index < pd.to_datetime('17-4-2014'))]

def create_dataset(df):
    dataX = []
    for c in df.columns:
        x = df.loc[:, c].as_matrix()
        dataX.append(x)
    return np.array(dataX), np.array(dataX)

#train_x, train_y = create_dataset(train)
#test_x, test_y = create_dataset(test)

#autoencoder = Sequential()
#autoencoder.add(Dense(output_dim=50, input_dim=250))
#autoencoder.add(Activation('tanh'))
#autoencoder.add(Dense(output_dim=250, input_dim=50))
#autoencoder.compile(loss='mean_squared_error', optimizer='rmsprop')
#autoencoder.fit(train_x, train_y, nb_epoch=1000, batch_size=10, verbose = 0)
#
#for i in range(train_x.shape[0]):
#    z = autoencoder.predict(train_x[i].reshape(1,250))
#    x = train_x[i]
#    if i < len(stox):
#        print (stox[i], np.sum(np.square(z-x)))
        
def create_dataset_index(df):
    dataX = []
    dataY = []
    for i in df.index:
        x = df.loc[i, stox].as_matrix()
        dataX.append(x)
        y = df.loc[i, '^DJI']
        dataY.append(y)
    return np.array(dataX), np.array(dataY)

#train = df[df.index < pd.to_datetime('04-01-2014')]
train_x, train_y = create_dataset_index(train)

model = Sequential()
model.add(Dense(output_dim=20, input_dim=30))
model.add(Activation('tanh'))
model.add(Dropout(0.1))
model.add(Dense(output_dim=10, input_dim=20))
model.add(Activation('tanh'))
model.add(Dropout(0.1))
model.add(Dense(output_dim=5, input_dim=10))
model.add(Activation('tanh'))
model.add(Dropout(0.1))
model.add(Dense(output_dim=1, input_dim=5))
model.compile(loss='mean_squared_error', optimizer='rmsprop')
model.fit(train_x, train_y, nb_epoch=2000, batch_size=50, verbose = 1)

def create_dataset_new_index(df):
    dataX = []
    dataY = []
    for i in df.index:
        x = df.loc[i, stox].as_matrix()
        dataX.append(x)
        y = df.loc[i, 'new_index']
        dataY.append(y)
    return np.array(dataX), np.array(dataY)

train_x, train_y = create_dataset_new_index(train)
new_model = Sequential()
new_model.add(Dense(output_dim=20, input_dim=30))
new_model.add(Activation('tanh'))
new_model.add(Dropout(0.1))
new_model.add(Dense(output_dim=10, input_dim=20))
new_model.add(Activation('tanh'))
new_model.add(Dropout(0.1))
new_model.add(Dense(output_dim=5, input_dim=10))
new_model.add(Activation('tanh'))
new_model.add(Dropout(0.1))
new_model.add(Dense(output_dim=1, input_dim=5))
new_model.compile(loss='mean_squared_error', optimizer='rmsprop')
new_model.fit(train_x, train_y, nb_epoch=2000, batch_size=50, verbose = 1)

df['pred'] = 0.0
df = df[df.index < pd.to_datetime('17-4-2014')]
for i in df.index:
     x = df.loc[i, stox].as_matrix()
     df.loc[i, 'pred'] = model.predict(x.reshape(1,30))
     
df['new_pred'] = 0.0
for i in df.index:
     x = df.loc[i, stox].as_matrix()
     df.loc[i, 'new_pred'] = new_model.predict(x.reshape(1,30))
     y = df.loc[i, '^DJI']
     
df['pred'] = en.inverse_transform(df['pred'])
df['new_pred'] = en.inverse_transform(df['new_pred'])
df['^DJI'] = en.inverse_transform(df['^DJI'])
df.to_hdf('DeepLearning.h5', 'Deep_Portfolio')
plt.plot(df['pred'], 'r', label = 'pred')
plt.plot(df['new_pred'], 'g', label = 'new_pred')
#plt.plot(en.inverse_transform(df['new_index']), 'b', label = 'new index')
plt.plot(df['^DJI'], 'k', label = 'index')
plt.legend()
plt.show()