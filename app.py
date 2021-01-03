################ Import Necessary Packages ################
import os
import sys
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import time 
import yfinance as yf
from fredapi import Fred
import quandl
import requests
from datetime import datetime, timedelta
import glob
from IPython.display import display

################ Website Setup ################
# Streamlit site configuration
st.set_page_config(
    page_title="Asset Allocator",
    layout="wide",
    initial_sidebar_state="auto"
)

# Real time data API keys
fred = Fred(api_key = "3e7ce9d3322d45b49f624720abd0f36a")
quandl.ApiConfig.api_key = "_gTGp-_JJ9kKR7-hCGT5"

################ Getting Predicted Data ################

# Getting all CSV files from ./prediction
all_files = glob.glob('prediction' + "/*.csv")

# Put all dataframe into a list
all_data = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=0, header=0)
    all_data.append(df)

# Concatenate all dataframes in all_data list, 
table = pd.concat(all_data, axis=1, ignore_index=False)

################ Getting Real-Time Data ################
## Get data
start = table.index[0]
test = '2020-12-01'
stock = yf.Ticker("^GSPC").history(start=test)
yields = quandl.get("USTREASURY/YIELD",start_date=test)
usd = yf.Ticker("DX-Y.NYB").history(start=test)
gold = quandl.get("LBMA/GOLD", start_date=test)
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
wti = pd.DataFrame(wti[wti.index>=test])
wti.columns = ["WTI"]
## Concat
table2 = pd.concat([stock,yields,usd,gold,wti], axis=1, ignore_index=False)

################ App Content ################

## Plotly chart for SPX
def plotting(pred, true):
    '''
    A function that plots both predicted values and true values
    '''
    for col in true.columns:
        fig = go.Figure(go.Scatter(
            x=true.index, 
            y=true[col],
            mode='lines',
            name=col.replace("_pred",""),
            line_color='Red',
            ))
        fig.add_trace(go.Scatter(
            x=pred.index, 
            y=pred[col+"_pred"],
            mode='lines',
            name=col + ' Prediction', 
            line_color='teal',
            ))

        fig.update_layout(
            height=500, 
            width=900,
            title = f"Monthly Forecast, {col}",
            title_font_size = 30, 
            title_x=0.5,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
            )
        st.write(fig)



################ Efficient Frontier ################
# Codes for Efficient Frontier were modified from: 
# https://github.com/PyDataBlog/Python-for-Data-Science

def EfficientFrontier(table):
### Populate portfolios
# Calculate daily and annual returns of the stocks
    returns_daily = table.pct_change()
    returns_quarterly = returns_daily.mean() * 21

    # Get daily and covariance of returns of the stock
    cov_daily = returns_daily.cov()
    cov_quarterly = cov_daily * 21

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

    ### Setup for plotting efficient frontier
    # find min Volatility & max sharpe values in the dataframe (df)
    min_volatility = df['Volatility'].min()
    max_sharpe = df['Sharpe Ratio'].max()

    # use the min, max values to locate and create the two special portfolios
    sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]
    min_variance_port = df.loc[df['Volatility'] == min_volatility]

    mv_port = min_variance_port.copy()
    ms_port = sharpe_portfolio.copy()
    for col in min_variance_port.columns:
        if col == 'Sharpe Ratio':
            pass
        else:
            mv_port[col] = mv_port[col].apply(lambda x: x*100)
            
    for col in sharpe_portfolio.columns:
        if col == 'Sharpe Ratio':
            pass
        else:
            ms_port[col] = ms_port[col].apply(lambda x: x*100)
    # plot frontier, max sharpe & min Volatility values with a scatterplot
    fig = px.scatter(
        df, 
        x="Volatility", 
        y="Returns",  
        size_max=60,
        color="Sharpe Ratio",
        color_continuous_scale = 'aggrnyl',
        
    )
    fig.add_scatter(
        x=sharpe_portfolio['Volatility'], 
        y=sharpe_portfolio['Returns'],
        mode="markers",
        marker={'size': 20,'color': "red",},
        showlegend=False
    )
    fig.add_scatter(
        x=min_variance_port['Volatility'], 
        y=min_variance_port['Returns'],
        mode="markers",
        marker={'size': 20,'color': "blue",},
        showlegend=False
    )
    fig.update_traces(textposition='top center')

    fig.update_layout(
        height=800,
        title_text='Portfolio'
    )
    pred_port = pd.concat([mv_port.T, ms_port.T], axis = 1)
    pred_port.columns = ['Minimum Volatility', 'Maximum Sharpe']
    return fig, pred_port




################ App Content ################
page_list = ["Forecast", "Predicted Optimal Portfolio", "True Optimal Allocatoin"]
page = st.sidebar.selectbox(
    "View",
    (page_list)
)
pred_fig, pred_port = EfficientFrontier(table)
true_fig, true_port = EfficientFrontier(table2)
if page == page_list[0]:
    st.title("Forecast Performance")
    st.write(plotting(table,table2))

if page == page_list[1]:
    
    st.title("Predicted Optimal Portfolio")
    st.write(pred_fig)
    st.write(pred_port)

if page == page_list[2]:
    st.title("True Optimal Portfolio")

    st.write(true_fig)
    st.write(true_port)