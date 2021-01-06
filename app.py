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

pure = pd.read_csv("prediction/pure_port.csv", index_col=0)

pred1 = pd.read_csv("prediction/pred1_port.csv", index_col=0)
true1 = pd.read_csv("prediction/true1_port.csv", index_col=0)

pred2 = pd.read_csv("prediction/pred2_port.csv", index_col=0)
true2 = pd.read_csv("prediction/true2_port.csv", index_col=0)

pred3 = pd.read_csv("prediction/pred3_port.csv", index_col=0)
true3 = pd.read_csv("prediction/true3_port.csv", index_col=0)

pred63 = pd.read_csv("prediction/pred63_port.csv", index_col=0)
true63 = pd.read_csv("prediction/true63_port.csv", index_col=0)

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

################ Compare Portfolio ################
def compare_portfolio(table,pred_port,true_port):
    result = true_port.copy()
    for col in pred_port.columns:
        pred_weights = list(pred_port.iloc[3:].loc[:,col])
        weights = [x/100 for x in pred_weights]
        returns_daily = table.pct_change()
        returns_quarterly = returns_daily.sum()

        # Get daily and covariance of returns of the stock
        cov_daily = returns_daily.cov()
        cov_quarterly = cov_daily * table.shape[0]


        weights = np.array(weights)
        weights /= np.sum(weights)
        returns = np.dot(weights, returns_quarterly)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_quarterly, weights)))
        sharpe = returns / volatility
        result[f"{col} Result"] = [returns*100, volatility*100, sharpe]+pred_weights
    col_order = ["Minimum Volatility", "Minimum Volatility Result", "Maximum Sharpe", "Maximum Sharpe Result"]
    result = result[col_order]
    return result

################ App Content ################
pure_fig, pure_port = EfficientFrontier(pure)

pred1_fig, pred1_port = EfficientFrontier(pred1)
true1_fig, true1_port = EfficientFrontier(true1)

pred2_fig, pred2_port = EfficientFrontier(pred2)
true2_fig, true2_port = EfficientFrontier(true2)

pred3_fig, pred3_port = EfficientFrontier(pred3)
true3_fig, true3_port = EfficientFrontier(true3)

pred63_fig, pred63_port = EfficientFrontier(pred63)
true63_fig, true63_port = EfficientFrontier(true63)

comp1 = compare_portfolio(
    table=table2[:21],
    pred_port=pred1_port,
    true_port=true1_port
)
comp2 = compare_portfolio(
    table=table2[21:42],
    pred_port=pred2_port,
    true_port=true2_port
)
comp3 = compare_portfolio(
    table=table2[42:63],
    pred_port=pred3_port,
    true_port=true3_port
)

comp4 = compare_portfolio(
    table=table2[:63],
    pred_port=pred63_port,
    true_port=true63_port
)

################ Page Layout ################
page_list = ["About", "Forecast", "Optimal Portfolio Month", "Optimal Portfolio Quarter"]
page = st.sidebar.selectbox(
    "View",
    (page_list)
)
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
    st.write("Here we have recommended allocations for each market based on prediction. We select the most optimal weighting based on the highest Sharpe Ratio. The Sharpe Ratio is the average return earned in excess of the risk-free rate (0 in our system) per unit of volatility or total risk. We have validation across different timeframes, all based on 21 trading days prediction.")
    st.title(f"Predicted Optimal Allocation, Next 21 Trading Days")
    st.write(pure_fig)
    st.write(pure_port)
    
    st.title(f"Optimal Allocation, {table2.index[42]} to {table2.index[62]}")
    st.write("Forecasted Optimal")
    st.write(pred3_fig)
    st.write("True Optimal")
    st.write(true3_fig)
    st.write(comp3)
    # st.write(comp3)

    st.title(f"Predicted Optimal Allocation, {table2.index[21]} to {table2.index[41]}")
    st.write("Forecasted Optimal")
    st.write(pred2_fig)
    st.write("True Optimal")
    st.write(true2_fig)
    st.write(comp2)
    # st.write(comp2)

    st.title(f"Predicted Optimal Allocation, {table2.index[0]} to {table2.index[20]}")
    st.write("Forecasted Optimal")
    st.write(pred1_fig)
    st.write("True Optimal")
    st.write(true1_fig)
    st.write(comp1)
    # st.write(comp1)

if page == page_list[3]:
    st.write("Here we have recommended allocations for each market based on 63 trading day prediction. We select the most optimal weighting based on the highest Sharpe Ratio. The Sharpe Ratio is the average return earned in excess of the risk-free rate (0 in our system) per unit of volatility or total risk.")
    st.title(f"Predicted Optimal Allocation, {table2.index[0]} to {table2.index[62]}")
    st.write("Forecasted Optimal")
    st.write(pred63_fig)
    st.write("True Optimal")
    st.write(true63_fig)
    st.write(comp4)