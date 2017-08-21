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
from sklearn.svm import SVR

np.random.seed(7)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore") 

df = pd.read_hdf('DeepLearning.h5', 'Data_Gold')


for c in df.columns:
    df[c+'_ret'] = df[c].pct_change().fillna(0)
svr_poly = SVR(kernel='poly', C=100, degree=2, verbose = 1)

look_back = 12
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

train_df = df.loc[df.index < pd.to_datetime('2016-01-01')]
val_df = train_df.loc[train_df.index >= pd.to_datetime('2013-01-01')]
train_df = train_df.loc[train_df.index < pd.to_datetime('2013-01-01')]
test_df = df.loc[df.index >= pd.to_datetime('2016-01-01')]

predictors = ['Gold']#, 'InterestRate']
train_x, train_y = create_dataset(train_df, look_back=look_back, columns = predictors)
val_x, val_y = create_dataset(val_df, look_back=look_back, columns = predictors)
test_x, test_y = create_dataset(test_df, look_back=look_back, columns = predictors)
svr_poly = svr_poly.fit(train_x, train_y)
#
#df.loc[:, 'Gold'] = sc.inverse_transform(df.loc[:, 'Gold'])
#df.loc[:, 'Pred'] = sc.inverse_transform(df.loc[:, 'Pred'])
#plt.plot(df.Gold,'y')
#plt.plot(df.Pred, 'g')

