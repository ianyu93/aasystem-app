import os
import sys
import streamlit as st
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import time 
import yfinance as yf
from fredapi import Fred
import quandl
import requests
from datetime import datetime, timedelta

fred = Fred(api_key = "3e7ce9d3322d45b49f624720abd0f36a")
quandl.ApiConfig.api_key = "_gTGp-_JJ9kKR7-hCGT5"
 
st.title('My first app')

true = yf.Ticker("^GSPC").history(start = '2020-12-01', period="1m")['Close']
time.sleep(1)

fig = go.Figure(go.Scatter(x=true.index, y=true,
                          mode='lines',
                          name='SPX 500',
                          line_color='Red'))

fig.update_layout(height=500, width=1000,
                  title = f"Quarterly Forecast, Forecasted On {datetime.today().strftime('%Y-%m-%d')}",
                  title_font_size = 30, title_x=0.5)

st.plotly_chart(fig)