################ Import Necessary Packages ################
import os
import sys
import numpy as np
import pandas as pd
import time 
import yfinance as yf
from fredapi import Fred
import quandl
import requests
from datetime import datetime, timedelta
import glob
from IPython.display import display
# Real time data API keys
fred = Fred(api_key = "3e7ce9d3322d45b49f624720abd0f36a")
quandl.ApiConfig.api_key = "_gTGp-_JJ9kKR7-hCGT5"

################ Getting Predicted Data ################

# Getting all CSV files from ./prediction
all_files = glob.glob('prediction' + "/*_prediction.csv")

# Put all dataframe into a list
all_data = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=0, header=0)
    all_data.append(df)

# Concatenate all dataframes in all_data list, 
table = pd.concat(all_data, axis=1, ignore_index=False)
table.index = pd.to_datetime(table.index)

################ Getting Real-Time Data ################
## Get data
start = table.index[0]
stock = yf.Ticker("^GSPC").history(start=start)
yields = quandl.get("USTREASURY/YIELD",start_date=start)
usd = yf.Ticker("DX-Y.NYB").history(start=start)
gold = quandl.get("LBMA/GOLD", start_date=start)
wti = pd.DataFrame(fred.get_series_latest_release(
    'DCOILWTICO'), columns=["price"])
time.sleep(1)
## Data Wrangling
stock = pd.DataFrame(stock['Close'])
stock.columns = ["SPX"]
yields = pd.DataFrame(yields['10 YR'])
yields.rename(columns={'10 YR': "10YR yields"}, inplace = True)
usd = pd.DataFrame(usd['Close'])
usd.columns = ["DXY"]
gold = pd.DataFrame(gold['USD (AM)'])
gold.rename(columns={'USD (AM)': "GOLD"}, inplace = True)
wti = pd.DataFrame(wti[wti.index>=start])
wti.columns = ["WTI"]

## Reindexing with date_range
date_range = pd.date_range(
    start = start,
    end = datetime.today(),  
    freq = 'B', 
    normalize = True
    )

# Reindexing with forward fill to fill new missing values with last valid observation
stock = stock.reindex(index=date_range, method='ffill')
usd = usd.reindex(index=date_range, method='ffill')
yields = yields.reindex(index=date_range, method='ffill')
wti = wti.reindex(index=date_range, method='ffill').fillna(method='ffill')
gold = gold.reindex(index=date_range, method='ffill')
## Concat
table2 = pd.concat([stock,yields,usd,gold,wti], axis=1, ignore_index=False)

## Align the column order as both tables have the same col name
table_col_order = table2.columns
table = table[table_col_order]


################ Efficient Frontier ################
# Codes for Efficient Frontier were modified from: 
# https://github.com/PyDataBlog/Python-for-Data-Science

def EfficientFrontier(table, name):
### Populate portfolios
# Calculate daily and annual returns of the stocks
    returns_daily = table.pct_change()
    returns_quarterly = returns_daily.sum()

    # Get daily and covariance of returns of the stock
    cov_daily = returns_daily.cov()
    cov_quarterly = cov_daily * table.shape[0]

    # Define selected assets
    selected = table.columns

    # Empty lists to store returns, volatility and weights of imiginary portfolios
    port_returns = []
    port_volatility = []
    sharpe_ratio = []
    stock_weights = []

    # Set the number of combinations for imaginary portfolios
    num_assets = len(selected)
    num_portfolios = 50000

    # Set random seed for reproduction's sake
    np.random.seed(101)

    # Populate the empty lists with each portfolios returns,risk and weights
    for single_portfolio in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, returns_quarterly)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_quarterly, weights)))
        sharpe = returns / volatility
        sharpe_ratio.append(sharpe)
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

    # A dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': port_returns,
                'Volatility': port_volatility,
                'Sharpe Ratio': sharpe_ratio}

    # Extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter,symbol in enumerate(selected):
        portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]

    # Make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)

    # Get better labels for desired arrangement of columns
    column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock+' Weight' for stock in selected]

    # Reorder dataframe columns
    df = df[column_order]
    df.dropna(how="any", inplace=True, axis=0)
    df.to_csv(f"prediction/{name}_port.csv")

table.to_csv("prediction/table.csv")
table2.to_csv("prediction/table2.csv")
EfficientFrontier(table=table[-21:], name="pure")
EfficientFrontier(table=table[21:42], name="pred")
EfficientFrontier(table=table2[21:42], name="true")