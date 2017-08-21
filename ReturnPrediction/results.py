# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 02:06:30 2017

@author: sonaa
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
plt.style.use('ggplot')
def returns():
    ty = pd.DataFrame(columns = ['dfname', 'title', 'fname'])
    ty.loc['DeepRegression'] = ['Pred_DeepRegression', 'Deep Regression Results', 'DeepRegression']
    ty.loc['ARIMA'] = ['Pred_ARIMA', 'ARIMA Results', 'ARIMA']
    ty.loc['CNN'] = ['Pred_CNN', 'CNN Results', 'CNN']
    ty.loc['VAR'] = ['Pred_VAR', 'VAR Results', 'VAR']
    ty.loc['LSTM'] = ['Pred_LSTM', 'LSTM Results', 'LSTM']
    
    for i in ty.index:
        df = pd.read_hdf('DeepLearning.h5', ty.loc[i, 'dfname'])
        
        train_df = df.loc[df.index < pd.to_datetime('2016-01-01')]
        test_df = df.loc[df.index >= pd.to_datetime('2016-01-01')]
#        mse = (train_df.Pred - train_df.Gold)
#        mse1 = (test_df.Pred - test_df.Gold)
#        print (i, sum(mse*mse), sum(mse1*mse1))
#        plt.figure(figsize=(20,20))
#        sns.tsplot(df.Gold, color = 'b', legend = 'Gold Prices')
#        sns.tsplot(train_df.Pred, color = 'r', legend = 'Insample Prediction')
#        sns.tsplot(test_df.Pred, color = 'g', legend = 'OUtsample Prediction')
        plt.plot(df.Gold, 'b', label = 'Gold Price')
        plt.plot(train_df.Pred, 'r', label = 'Insample Prediction')
        plt.plot(test_df.Pred, 'g', label = 'Outsample Prediction')
        plt.title(ty.loc[i, 'title'])
        plt.legend()
        plt.savefig(ty.loc[i, 'fname']+'.png')
        plt.show()

def portfolio():
    df = pd.read_hdf('DeepLearning.h5', 'Deep_Portfolio')
    train_df = df.loc[df.index < pd.to_datetime('2014-01-01')]
    test_df = df.loc[df.index >= pd.to_datetime('2014-01-01')]
#    plt.figure(figsize=(20,20))
    plt.figure()
    plt.plot(df['^DJI'], 'b', label = 'Index')
    plt.plot(train_df.pred, 'r', label = 'Insample Prediction')
    plt.plot(test_df.pred, 'g', label = 'Outsample Prediction')
    plt.title('Deep Index')
    plt.legend()
    plt.savefig('port1.png')
#    plt.figure(figsize=(20,20))
    plt.figure()
    plt.plot(df['^DJI'], 'b', label = 'Index')
    plt.plot(train_df.new_pred, 'r', label = 'Insample Prediction')
    plt.plot(test_df.new_pred, 'g', label = 'Outsample Prediction')
    plt.title('Smart Portfolio')
    plt.legend()
    plt.savefig('port2.png')
#returns()
portfolio()