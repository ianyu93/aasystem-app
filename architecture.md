# **Architecutre**

Here is an overview of what I did for Feature Engineering and the Neural Network architecture. More details will be provided once I finish documenting the scripts and upload to GitHub. 

---
### **Feature Engineering**
In my dataset, not only did I include market values across asset classes, but I also manually engineered many indicators that blew out into 200+ features. While I'm not going to list everything here, my goal was to measure 4 things: yield curve, momentum, relative strength, and volatility.

**Yield Curve**

In the dataset, not only did I include treasury yields for multiple maturity, but I also created features to include yield difference between different pairs of maturity. For example, `10YR yields - 2YR yields` is the difference for the 2Y/10Y pair. Replicating to other pairs, the dataset would see whether the differences are getting steeper or flatter, providing a proxy to the yield curve development.

**Momentum**

To measure momentum, I used Exponential Moving Average, or EMA. While Simple Moving Average (SMA, the regular moving average) smooths out the overall trend line, EMA adds more weight on more recent values. In other words, EMA not only shows the overall trend, it also incorporates latent momentum. We will be applying EMA on other features to learn momentum of other features.

*Note: I used pandas Exponential Weighted Functions, which works slightly different from the traditional EMA in the finance world, but serves our purpose.*

**Cross-Market Relative Strength**

To measure cross-market relative strength, I used Relative Strength Line. A concept frequently used by John Murphy in Intermarket Analysis, the RSL is simply the ratio between any two given assets/markets. It measures the relative performance of the two assets. For example, SPX/US10Y RSL measures the relative performance of the stock market comparing to the 10 Year Treasury Bond. An increase of this indicator would signal that the stock market's relative performance to the bond market is getting stronger.

**Volatility**

To measure volatility, I used the Bollinger Band indicator. The Bollinger Band is comprised of a middle band of SMA, typically a 20-Day Moving Average, an upper band of +2 standard deviation from the middle band, and -2 standard deviation from the middle band. Approximately 90% of the price action would happen within the bands, and since standard deviation is a measure of volitility, when the market becomes volitile, the bands would expand, and vice versa when the market becomes more stable.

**Timeframe**

For each of the ascribed feature, I also incorporated certain timeframes. For moving averages, we will use 5 (trading days) to measure weekly moving average, 20 (4 weeks of trading days) to represent monthly, and 60 (3 months) to represent a quarter. I also employed market convention of 50-day and 200-day moving averages to measure long-term trends, despite the fact that they do not represent an intuitive timeframe. Contrary to popular belief, the heavy focus of the quantitative perspective in the financial world is actually relatively new (starting around the 80s). Many of the convention are just hard-tested rules that lasted for decades.

---
### **Neural Network**

In a nutshell, our model architecture looks like this:

<div>
<Center>
<img src="https://imgur.com/mUESztw.png" height=400>
</div>

**Recurrent Neural Netowrk** is a type of neural network that allows us to learn backwards in sequence. It takes in a 3D shape array, input the data as (batch size, sequence, features). Batch size would be the number of data points that we are passing into the neural network at once. If we have a batch size of 1024, then we are passing 1024 trading days into the network at a time. We will have the hypertuner to determine what is the optimal batch size. Sequence length is about the past context, where if we set a sequence length of 10, the model would learn how does the previous 10 sequence affect the current input. We will also leave it to the hypertuner to determine the best sequence length parameter. Features dimension would simply be the number of features we have in our dataset.
<div>
<Center>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Recurrent_neural_network_unfold.svg/2880px-Recurrent_neural_network_unfold.svg.png" height=400>
</div>
<div>
<Center>

*image from [Wikepedia](https://en.wikipedia.org/wiki/Recurrent_neural_network#/media/File:Recurrent_neural_network_unfold.svg)*
</div>

**Long Short-Term Memory** is a special type of RNN that learns about the long term default behaviour of the dataset. In effect, this would decompose seasonality, trends, and other potential long-term patterns. 

**Bidirectional** is applied to the LSTM RNN for the purpose of learning the future context as well. Not only does the past affect the stock market today, but also the anticipation of tomorrow's environment would affect today's market. Therefore, we would also need to understand how that anticipation affects today's price. The bidirectional element creates a separate network in the same training session that learns forwards in the sequence instead, so that each time the network is learning both backwards and forward in time. 

**Time Distributed Layer** is a special type of output layer that keeps the training input and output one at a time, keeping the timestamps true. Without the layer, the default behaviour of RNN would learn and output in batches instead. 

