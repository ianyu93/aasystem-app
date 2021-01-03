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
page_list = ["Forecast", "Optimal Portfolio"]
page = st.sidebar.selectbox(
    "View",
    (page_list)
)
pred_fig, pred_port = EfficientFrontier(pred)
true_fig, true_port = EfficientFrontier(true)
pure_fig, pure_port = EfficientFrontier(pure)
if page == page_list[0]:
    st.title("Forecast Performance")
    st.write(plotting(table,table2))

if page == page_list[1]:
    st.title("Predicted Optimal Portfolio, Next 21 Trading Days")
    st.write(pure_fig)
    st.write(pure_port)

    st.title("Predicted Optimal Portfolio, Continuous")
    st.write(pred_fig)
    st.write(pred_port)

    st.title("True Optimal Portfolio, Continuous")
    st.write(true_fig)
    st.write(true_port)