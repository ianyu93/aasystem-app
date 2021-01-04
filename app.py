################ Import Necessary Packages ################
import os
import sys
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time 
import yfinance as yf
from datetime import datetime, timedelta
from PIL import Image

################ Website Setup ################
# Streamlit site configuration
st.set_page_config(
    page_title="Asset Allocator",
    layout="wide",
    initial_sidebar_state="auto")
################ Getting All Data ################

table = pd.read_csv("prediction/table.csv", index_col=0)
table2 = pd.read_csv("prediction/table2.csv", index_col=0)
pred = pd.read_csv("prediction/pred_port.csv", index_col=0)
true = pd.read_csv("prediction/true_port.csv", index_col=0)
pure = pd.read_csv("prediction/pure_port.csv", index_col=0)


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
            name=col,
            line_color='Red',
            ))
        fig.add_trace(go.Scatter(
            x=pred.index, 
            y=pred[col],
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

def EfficientFrontier(df):
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
page_list = ["About", "Forecast", "Optimal Portfolio"]
page = st.sidebar.selectbox(
    "View",
    (page_list)
)
pred_fig, pred_port = EfficientFrontier(pred)
true_fig, true_port = EfficientFrontier(true)
pure_fig, pure_port = EfficientFrontier(pure)
page_bg_img = Image.open("img/newplot.png")

if page == page_list[0]:
    st.title("About the Project")
    st.write("Hi, my name is Ian, and this is my first Data Science project, an Asset Allocation System. The system comprises of two parts. First, it utilizes neural networks to forecast the values for 5 major financial markets in the next 23 trading days.  Then, based on the predicted values of the major financial markets, forecast the optimal weight of allocation to each major markets. The allocation of the model is based on Efficient Frontier, which holds the assumption that investors prefer the maximizing return with the least amount of risk. ")
    st.write("The project is inherently exploratory with limitations, more information will be updated before January 14, 2021. It was based on my 2-week exploration on stock market forecast with intermarket analysis, which is still on GitHub [here](https://github.com/ianyu93/stock-market-forecast). All the scripts for this system will soon be updated. In the meantime, check out my [personal homepage](https://ianyu93.github.io/homepage/).")
    st.image(page_bg_img)

if page == page_list[1]:
    st.title("Forecast Performance")
    st.write("Here you will see the performance of my system in forecasting each of the major assets, where I used S&P 500, US 10 Year Treasury Yields, Gold, WTI Oil, and the Dollar Index as my proxies. As my models were not trained beyond 63 trading days before the monthly forecast, or my test set, the charts comprise both the predicted values for 63 trading days before the monthly forecast date, and 21 trading days after. The true value will be updated daily, until the next forecast date.")
    st.write(plotting(table,table2))

if page == page_list[2]:
    st.write("Here we have a recommended allocation for each market based on prediction. We select the most optimal weighting based on the highest Sharpe Ratio. The Sharpe Ratio is the average return earned in excess of the risk-free rate (0 in our system) per unit of volatility or total risk. ")

    st.title("Predicted Optimal Allocation, Next 21 Trading Days")
    st.write("This is based on our predicted values for each market for the next 21 tradings after the forecast date. This represents pure speculation of the future values without considering past values and inherently includes more uncertainty.")
    st.write(pure_fig)
    st.write(pure_port)

    st.title("Predicted Optimal Allocation, Continuous")
    st.write("This is based on our predicted values of the past 63 trading days and next 21 trading days. This is equivalent of continuously update daily on portfolio weighting based on the past 63 trading days as well as predicted values of next 21 trading days. Currently such pipeline is still in design.")
    st.write(pred_fig)
    st.write(pred_port)

    st.title("True Optimal Allocation, Continuous")
    st.write("This is based on true values of the past 63 trading days as well as the next 21 trading days. As the next 21 trading days is still in the future, this chart will be updated daily when the true price is updated. ")
    st.write(true_fig)
    st.write(true_port)