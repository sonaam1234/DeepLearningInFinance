# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 09:17:04 2017

@author: sonaa
"""

#!/usr/bin/env python

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import pytz
import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime
from pandas_datareader import data, wb


SITE = "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
START = datetime(1960, 1, 1, 0, 0, 0, 0, pytz.utc)
END = datetime.today().utcnow()


def scrape_list(site):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site, headers=hdr)
    page = urllib2.urlopen(req)
    soup = BeautifulSoup(page)

    table = soup.find('table', {'class': 'wikitable sortable'})
    sector_tickers = dict()
    for row in table.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 0:
            sector = str(col[3].string.strip()).lower().replace(' ', '_')
            ticker = str(col[0].string.strip())
            if sector not in sector_tickers:
                sector_tickers[sector] = list()
            sector_tickers[sector].append(ticker)
    return sector_tickers


def download_ohlc(sector_tickers, start, end):
#    sector_ohlc = {}
    for sector in sector_tickers.keys():
        tickers = sector_tickers[sector]
        print (sector)
        for ticker in tickers:
            print ('Downloading data from Yahoo for %s' % ticker)
            try:
                data1 = data.DataReader(ticker, 'yahoo', start, end)
    #            for item in ['Open', 'High', 'Low']:
    #                data1[item] = data1[item] * data1['Adj Close'] / data1['Close']
    #            data1.rename(items={'Open': 'open', 'High': 'high', 'Low': 'low',
    #                               'Adj Close': 'close', 'Volume': 'volume'},
    #                        inplace=True)
    #            data1.drop(['Close'], inplace=True)
                sector_ohlc[ticker] = data1['Adj Close']   
                sector_olhlc[ticker].columns = ticker
            except:
                print (ticker, 'Not found')
    print ('Finished downloading data')
    return sector_ohlc


def store_HDF5(sector_ohlc, path):
    with pd.get_store(path) as store:
        for sector in sector_ohlc.keys():
            ohlc = sector_ohlc[sector]
            store[sector] = ohlc


if __name__ == '__main__':
    l = pd.read_csv('comp.csv')
    df = pd.DataFrame()
    for i in l.index:
        sym = l.loc[i, 'Symbol']
        data1 = data.DataReader(sym, 'yahoo', START, END)['Adj Close']
        data1 = pd.DataFrame(data1)
        data1.columns = [sym]
        if df.empty:
            df = data1
        else:
            df = pd.concat([df, data1], axis=1)
df = df.dropna()
df.to_csv('dji.csv')
#    sector_tickers = scrape_list(SITE)
#    sector_ohlc = download_ohlc(sector_tickers, START, END)
#    df = pd.DataFrame()
#    for k in sector_ohlc.keys():
#        if df.empty:
#            df = pd.DataFrame(sector_ohlc[k])
#            df.columns  = [k]
#        else:
#            ef = pd.DataFrame(sector_ohlc[k])
#            ef.columns  = [k]
#            df = pd.concat([df,ef],axis=1)
#        
#    df.to_hdf('DeepLearning.h5', 'Data_Index', table = True)
##    df = pd.DataFrame(sector_ohlc.items())