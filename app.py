################ Import Necessary Packages ################
import os
import sys
from pathlib import Path
from PIL import Image
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px
import time 
import yfinance as yf
import base64

################ Website Setup ################
# Streamlit site configuration
st.set_page_config(
    page_title="Asset Allocator",
    layout="centered",
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

################ Define Functions ################
## Read markdown for web content
def read_markdown_file(markdown_file):
    '''
    A function that reads markdown files for streamlit, copied from:
    https://pmbaumgartner.github.io/streamlitopedia/markdown.html
    '''
    return Path(markdown_file).read_text()

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    return base64.b64encode(img_bytes).decode()

## Plotly chart for SPX
def plotting(pred, true):
    '''
    A function that plots both predicted values and true values
    '''
    for col in true.columns:
        y_true = true[col]
        y_pred = pred[col][:len(true[col])]
        mse = mean_squared_error(y_true, y_pred)
        rmse = math.sqrt(mse)
        nrmse = rmse / y_true.mean()
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
            height=388, 
            width=700,
            title = f"Monthly Forecast, {col}, NRMSE: {nrmse*100:0.2f}%",
            title_font_size = 25, 
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
        if col != 'Sharpe Ratio':
            mv_port[col] = mv_port[col] * 100

    for col in sharpe_portfolio.columns:
        if col != 'Sharpe Ratio':
            ms_port[col] = ms_port[col] * 100
    # plot frontier, max sharpe & min Volatility values with a scatterplot
    fig = px.scatter(
        df, 
        x="Volatility", 
        y="Returns",  
        size_max=60,
        color="Sharpe Ratio",
        color_continuous_scale = 'aggrnyl',
        hover_data=df.columns

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
        title_text=f"Max Sharpe return is {(sharpe_portfolio['Returns'] * 100).values} %",
    )
    pred_port = pd.concat([mv_port.T, ms_port.T], axis = 1)
    pred_port.columns = ['Min. Vol', 'Max Sharpe']
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
    col_order = ["Min. Vol", "Min. Vol Result", "Max Sharpe", "Max Sharpe Result"]
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
page_list = ["About","Forecast", "Optimal Portfolio Monthly", "Optimal Portfolio Quarterly","Architecture", "Future Development"]
page = st.sidebar.selectbox(
    "View",
    (page_list)
)
# page_bg_img = Image.open("img/newplot.png")

predict_list = [
    f"{table.index[63]} to {table.index[-1]}",
    f"{table.index[42]} to {table.index[62]}",
    f"{table.index[21]} to {table.index[41]}",
    f"{table.index[0]} to {table.index[20]}"
]

if page == page_list[0]:
    about = read_markdown_file("about.md")
    st.markdown(about, unsafe_allow_html=True)

if page == page_list[1]:
    st.title("Forecast Performance")
    st.write(f"Here is the forecast performance of the AASystem. The system has been continuously predicting each market with data from 21 trading days ago, and has not seen any data from {table.index[0]}. The model has predicted values up to {table.index[-1]}, and the true value for each market will be updated daily until then. For each graph, a [Normalized Root-Mean-Squared-Error by Mean](https://www.marinedatascience.co/blog/2019/01/07/normalizing-the-rmse/) is displayed in percentage, where lower values indicate less residual variance.")
    st.write(plotting(table,table2))

if page == page_list[2]:
    how = about = read_markdown_file("how.md")
    timeframe = st.selectbox("Choose a Timeframe", predict_list)
    if timeframe == predict_list[0]:
        st.title("Optimal Allocation, Next 21 Days")
        st.write(pure_port)
        st.write(pure_fig)
    if timeframe == predict_list[1]:
        st.title("Optimal Allocation")
        st.write(comp3)
        st.write("Select Forecasted ")
        if st.checkbox('Forecasted Optimal Efficient Frontier'):
            st.write("Forecasted Optimal")
            st.write(pred3_fig)
        if st.checkbox("True Optimal Efficient Fronter"):
            st.write("True Optimal")
            st.write(true3_fig)
    if timeframe == predict_list[2]:
        st.title("Optimal Allocation")
        st.write(comp2)
        if st.checkbox('Forecasted Optimal Efficient Frontier'):
            st.write("Forecasted Optimal")
            st.write(pred2_fig)
        if st.checkbox("True Optimal Efficient Fronter"):
            st.write("True Optimal")
            st.write(true2_fig)
            # st.write(comp2)
    if timeframe == predict_list[3]:
        st.title("Optimal Allocation")
        st.write(comp1)
        if st.checkbox('Forecasted Optimal Efficient Frontier'):
            st.write("Forecasted Optimal")
            st.write(pred1_fig)
        if st.checkbox("True Optimal Efficient Fronter"):
            st.write("True Optimal")
            st.write(true1_fig)
            # st.write(comp1)
    st.markdown(how)
    header_html = f"""<img src='data:image/png;base64,{img_to_bytes("img/mpt-image-2.jpg")}' class='img-fluid' height=500>"""
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("*How to find Efficient Frontier, image from [guidedchoice.com](https://www.guidedchoice.com/video/dr-harry-markowitz-father-of-modern-portfolio-theory/)*")

if page == page_list[3]:
    st.title("Optimal Allocation")
    st.write("Please refer to 'Optimal Portfolio Monthly' for how to read the charts. Here we also compare the true optimal weighting against the AASystem's choice for the last 63 trading days, but here the system predicted 63 trading days, or a quarter, in advance.")
    st.title(f"{table2.index[0]} to {table2.index[62]}")
    st.write(comp4)
    if st.checkbox('Forecasted Optimal Efficient Frontier'):
        st.write("Forecasted Optimal")
        st.write(pred63_fig)
    if st.checkbox("True Optimal Efficient Fronter"):
        st.write("True Optimal")
        st.write(true63_fig)

if page == page_list[4]:
    architecture = read_markdown_file("architecture.md")
    st.markdown(architecture, unsafe_allow_html=True)

if page == page_list[5]:
    future = read_markdown_file("future.md")
    st.markdown(future, unsafe_allow_html=True)