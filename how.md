## **Predcited vs. True Optimal Weighting**

The AASystem recommends a set of weightings across the asset classes based on predicted values for the month, but we also want to compare how would we perform if we were to follow the AASystem's advice. 

There are 4 timeframes that you can select. By default, the latest forecast is displayed and cannot be compared yet, but you can also select the last 3 timeframes and compare the true and predicted optimal weighting.

**True Optimal Weighting:** Based on true value throughout the timeframe

**Result** Performance of the system's recommended weigting if we were to invest based on recommendation.

---

### **How to Read the Table**

|Portfolio Weighting|Description|
|---|---|
|**Min. Vol:** |True optimal portfolio weighting, given the goal is to seek minimum volatility.|
|**Min. Vol Result:**|Performance Optimal portfolio weighting provided by the system.|
|**Max Sharpe:**|True optimal portfolio weighting, given the goal is to seek maximum Sharpe ratio.|
|**Max Sharpe Result:**|Performance Optimal portfolio weighting provided by the system.|
|*Metrics*|*Description*|
|*Returns:*| Returns of the portfolio in percentage|
|*Volatility:*| Volatility of the portfolio in percentage|
|*Sharpe Ratio:*| [Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp) is the measure of returns for each unit of volatility.|
|*Asset Weighting:*| Weighting for each asset class in a given portfolio|

---




### **Efficient Frontier Interactive Graph**

If neither the Min. Vol nor the Max Sharpe weighting satifies your need, you can examine other weightings along the Efficient Frontier through the interactive chart. Select *Forecasted Optimal Efficient Frontier* for what the AASystem prediced and *True Optimal Efficient Frontier* to compare.

### **Acknowledgement**
The codes to calculate and plot the Efficient Frontier was modified from [here](https://github.com/PyDataBlog/Python-for-Data-Science).
