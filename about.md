# **Welcome to the AASystem**

When it comes to applying AI in investment, the most obvious application would be predicting the stock market. After all, that is "where the money is made". Predicting the stock market, however, is inherently hard and risky. Even if one can create a model that forecasts relatively well, what is the next step? How much money should one invest? How does one control the risks to protect downside? In the financial world, not only does security selection matter, but diversification through asset allocation also matters. Asset allocation is not confined within the stock market world only, but also across different financial markets, such as currency, commodity, and the bond market. 

The AASystem, my Asset Allocation System, does exactly that in two parts:

1. First, AASystem performs monthly and quarterly forecast of the price movement across different financial markets. 
2. Then, based on the predicted values across different markets, the system allocates weightings across different asset classes that maximizes return while minimizing risks. 

**Essentially, the AASystem tells me how much money should I put in stocks, bonds, gold, oil, and dollars market to maximize my return while minimizing risks next month/quarter**. 

<div>
<Center>
<img src="https://imgur.com/q4wCxCZ.png" height=225 alt="Two parts of the the AASystem">
</div>

---
### **How is AASystem Different?**

The AASystem is different in two ways: How the prediction problem is framed and how allocation weigting is decided.

From the many predictive models on the web, there are two approaches. First is to predict specific stock or the S&P 500 itself with their past data. This approach is confined within the stock world and is turning a blind eye to the macro economy and financial trends, making it hard to forecast for a longer timeframe. The second approach is to transform the Closing price 30 days later into binary classes of price increased or not, create technical indicators as additional features, and predicts based on today's prices and the indicators. This approach often ignores the temporal affect on the market. 

For asset allocation, based on Modern Portfolio Theory, the typical approach is to annualize the returns and volatility based on past history, making an assumption of the future. Instead the AASystem attempts to allocate based on the predicted future, controlling the risks that it foresees.

---
### **Major Concepts**

The AASystem is built on two major financial concepts: **Intermarket Analysis and Efficient Frontier**.

[Intermarket Analysis](https://www.investopedia.com/terms/i/intermarketanalysis.asp#:~:text=Intermarket%20analysis%20is%20a%20method,be%20beneficial%20to%20the%20trader.) is a method of analyzing markets by examining the correlation between different asset classes. The pioneer of the discipline, John J. Murphy, asserts that the four major markets - Stocks, Bonds, Commodity, and Currency - are intercorrelated and can be examined in parallel to gain long-term insights.

[Efficient Frontier](https://www.investopedia.com/terms/e/efficientfrontier.asp#:~:text=The%20efficient%20frontier%20is%20the,for%20the%20level%20of%20risk.), the cornerstone of the [Modern Portfolio Theory](https://www.investopedia.com/terms/m/modernportfoliotheory.asp), seeks the a set of optimal asset weightings that offer the highest expected return for a defined level of risk or the lowest risk for a given level of expected return. The weighting of different assets does not only consider the expected returns and volatility of each asset, but also the covariance between the assets. 

<div>
<Center>
<img src="https://school.stockcharts.com/lib/exe/fetch.php?media=market_analysis:intermarket_analysis:im-1-intermarket.png" height=500 alt="Bond Market and the Stock Market have inverse relationship">
<img src="https://imgur.com/pL1ftkb.png" height=500 alt="Bond Market and the Stock Market have inverse relationship">
</div>
<div>
<Center>

*A: Bond Market and the Stock Market have inverse relationship. B: Efficient Frontier*
</div>

---
### **System Flow Breakdown**

The AASystem automated workflow is split into 6 stages, from sourcing and cleaning the data all the way to making prediction.

**Stage 1: Sourcing and Cleaning.** At stage 1, the AASystem sources data from the [Yahoo! Finance](http://yahoo.finance/), [Quandl](https://www.quandl.com/), and [FRED](https://fred.stlouisfed.org/) through APIs. The data collected includes daily values for S&P 500, Treasury Yields for various maturity, WTI Oil Sport Price, Gold Spot Price, the Dollar Index, and an annual growth rate for US Consumer Price Index. The system treats missing values, realign timestamps, and concatenates into a single dataframe appropriate to the model. 

**Stage 2: Feature Engineering.** At stage 2, the AASystem takes in the cleaned dataframe, feature engineers multiple technical indicators to measure relative strength between any two assets, momentum, and volatility. The system then creates a training dataset and a final testing dataset for both monthly and quarterly trading day prediction. 

**Stage 3: Hypertuning.** At stage 3, data of the last 20 years are fed into the hypertuner to search the best predictive parameters in the neural network models for each of the market. This step usually takes 6-8 hours and takes place every year.

**Stage 4: Training.** As the parameters are determined at Stage 3, the AASystem will train each predictive model based on the given parameters. This step usually takes 1 hour and takes place every month.

**Stage 5: Forecasts.** Once the models are trained, the final testing dataset from Stage 2 is fed in to make forecast. The forecast includes 63 trading days before the forecast date that the models have never seen before, and predicting one month/quarter after the forecast date. This step takes place every month, after training.

**Stage 6: Asset Allocation.** Based on the predicted values, the AASystem makes a set of recommendations based on the predicted values. This website is updated daily to compare true market value and forecasted values. 

<div>
<Center>
<img src="https://imgur.com/8s3Ht7h.png" height=180 alt="Bond Market and the Stock Market have inverse relationship">

*Tools Used in the Project*
</div>

---
### **Limitations**
The AASystem is currently limited to market-level allocation, controlling investment risks from the macro-level. The actual returns and volatility are still subject to securities selection and allocation in each market. The subsystem that performs securities selection and allocation in each market will continue to be developed.

The evaluation metrics on Optimal Portfolio assume a buy-and-hold scenario from investors. In practice, buy-and-hold strategy rarely lasts only a month. I will also continue to optimize the predictive models to improve longer-term forecasts. The model also does not consider weight cap, such as maximum weighting for a given market should be X%. 

---
### **Acknowledgement and Notes**

The AASystem was built over 4 weeks from scratch. In the first 2.5 weeks, I performed an preliminary project that sought to explore how to forecast the S&P 500 through Long Short-Term Memory Recurrent Neural Network, and [here is its GitHub link](https://github.com/ianyu93/stock-market-forecast/tree/master). After a successful epxloration, I replicated the same model to other major asset classes, designed an automated pipeline to hypertune parameters every year, train every month, and update daily for this web app. The complete pipeline will soon be updated to GitHub, so stay tuned!