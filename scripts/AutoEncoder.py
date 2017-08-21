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

df = pd.read_hdf('DeepLearning.h5', 'Data_Index')

ind = '^DJI'

stox = list(df.columns)
stox.remove(ind)

s = df['^DJI'].dropna()
sc = Normalizer()
s.loc[:] = sc.fit_transform(s)[0]

look_back = 2
timeseries = np.asarray(s)
timeseries = np.atleast_2d(timeseries)
if timeseries.shape[0] == 1: timeseries = timeseries.T
X = np.atleast_3d(np.array([timeseries[start:start + look_back] for start in range(0, timeseries.shape[0] - look_back)]))
y = X

predictors = ['Gold']#, 'DJI','Inflation']#, 'InterestRate']
m = Sequential()
m.add(LSTM(5, input_dim=1, return_sequences=True))
m.add(LSTM(1, return_sequences=True))
m.add(Activation('linear'))
m.compile(loss="mse", optimizer="rmsprop")
m.fit(X, y, epochs=1000, batch_size=80, verbose=1, shuffle=False)

for i in range(len(df.index)):
    if i <= look_back:
        continue
    a = s.loc[s.index[i-look_back:i]].as_matrix()
    y = m.predict(a.reshape(1,look_back,1))