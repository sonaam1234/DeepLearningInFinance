# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 09:34:09 2017

@author: sonaa
"""

import warnings
warnings.filterwarnings("ignore")
from scipy import stats
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA
import statsmodels.tsa.api as sm
import statsmodels.formula.api as sf
import numpy as np
from arch import arch_model
import pandas as pd
from pandas_datareader import data, wb
import sklearn.linear_model as linear_model
import sklearn.metrics as metrics
import sklearn.svm as svm
import datetime

start = datetime.datetime(1960, 1, 1)
end = datetime.datetime(2017, 3, 27)

IR=data.DataReader("FEDFUNDS", "fred", start, end) 
inflation=data.DataReader("CPIAUCSL", "fred", start, end)
reserves=data.DataReader("ADJRESSL", "fred", start, end)
gold=data.DataReader("GOLDAMGBD228NLBM", "fred", start, end)
gold= gold.resample('D').pad().loc[IR.index, :].fillna(method='ffill')
dji=data.DataReader('^DJI', 'yahoo', start, end).resample('D').pad()
dji = dji.loc[IR.index, :].fillna(method='ffill')['Adj Close']

df = pd.DataFrame()
df = pd.concat([gold, dji, IR, inflation, reserves], axis=1)
df.columns = ['Gold','DJI','InterestRate','Inflation','Reserves']
df = df.dropna()

df.to_hdf('DeepLearning.h5', 'Data_Gold', table = 1)