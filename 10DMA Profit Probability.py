# %% [markdown]
# # 10 Day Moving Average Stock Profit Probability

# %% [markdown]
# The purpose of this notebook is to scan the stock market for stock that have a certain probability of returning a positive profit trading above the 10 day moving average. Instead of using the entire market, this dataset has the top 600 publicly listed companies by market cap.

# %%
# importing packages
import yfinance as yf
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

# importing list of stocks
stocks = pd.read_csv("C:\\Users\\12104\\OneDrive\\Desktop\\List of Stocks.csv")
stocks # this is just used for iterating over the tickers, not live data

# %% [markdown]
# # Your Parameters
# This program is set up to return stocks that make a specific probability of positive returns trading above the 10 day moving average. This program is dependent on 2 main parameters, plus one optional:
# 
# "past_days" the amount of the days into the past. For example, putting 365 would give you info on the past year. 
# 
# "prob" is your desired probability as a percent. 
# 
# "tick" shows you an individual stock's price history, 10 day moving average, and probability of positive profit over the 10DMA

# %%
# enter your prefered timeframe in days in the parenthesis:
past_days = (180)

# enter your prefered probability of a positive profit:
prob = (60)

# ticker for individual stock
tick = 'SPY'

# %%
# Setting time periods: today, one year ago
current_date = dt.datetime.now() - dt.timedelta(days=1)
one_pa = current_date - dt.timedelta(days=past_days) # for the price 
one_pa_ma = one_pa - dt.timedelta(days=10) # add 10 days to whatever period to makeup for delay in moving average

# formatting
time_n = current_date.strftime("%Y-%m-%d")
time_nm1 = one_pa.strftime("%Y-%m-%d")
time_nm1_ma = one_pa_ma.strftime("%Y-%m-%d")

# %% [markdown]
# # Testing Individual Stocks
# Below shows a function that returns a chart of the price history with the 10 day moving average. Underneath, it shows the % probability of returning a positive profit at the specified timeframe. 

# %%
# enter ticker symbol in the quotes

enter_stock = tick # enter stock choice here

# setting up the data
stock_data = yf.download(enter_stock, start=time_nm1, end=time_n)
stock_data_ma = yf.download(enter_stock,start=time_nm1_ma, end=time_n)
stock_data['10DMA'] = stock_data_ma['Close'].rolling(window=10).mean()

# showing the price history and DMA
fig = px.line(
                 stock_data, 
                 y="Close", 
                 title=enter_stock, 
                 color_discrete_sequence=['red','blue'],
                 template="plotly_dark")

fig.add_trace(px.line(
                 stock_data, 
                 y='10DMA').data[0]
                 )

fig.update_layout( 
                 title=enter_stock,
                 xaxis_title='Date',
                 yaxis_title='Price in $',
                 showlegend=True
                 )
fig.show()

# %%
def calculate_profit(ticker_symbol):
    # Define the start and end dates for the historical data
    start_date = time_nm1
    end_date = time_n
    
    # Fetch historical data from Yahoo Finance
    data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Calculate the 10-day moving average
    data['10_day_ma'] = data['Close'].rolling(window=10).mean()

    # Initialize variables
    total_profit = 0
    is_in_position = False
    trades = []
    total_trades = 0
    positive_trades = 0

    # Iterate over the data to analyze the crossing of the moving average
    for i in range(1, len(data)):
        current_close = data['Close'].iloc[i]
        previous_close = data['Close'].iloc[i - 1]
        current_ma = data['10_day_ma'].iloc[i]
        previous_ma = data['10_day_ma'].iloc[i - 1]

        # Check for the crossing above the 10-day moving average
        if previous_close < previous_ma and current_close > current_ma:
            if not is_in_position:
                buy_price = current_close
                is_in_position = True
                trades.append({'Date': data.index[i], 'Action': 'Buy', 'Price': buy_price, 'Profit': 0})
                total_trades += 1

        # Check for the crossing below the 10-day moving average
        elif previous_close > previous_ma and current_close < current_ma:
            if is_in_position:
                sell_price = current_close
                profit = sell_price - buy_price
                total_profit += profit
                is_in_position = False
                trades.append({'Date': data.index[i], 'Action': 'Sell', 'Price': sell_price, 'Profit': profit})
                if profit > 0:
                    positive_trades += 1

    # Calculate the probability of a positive trade
    probability = (positive_trades / total_trades) * 100 if total_trades > 0 else 0

    return total_profit, trades, probability

# Define the ticker symbol of the stock
ticker_symbol = tick

# Calculate the total profit, trades, and probability
profit, trades, probability = calculate_profit(ticker_symbol)

# Print the total profit
print(f"Total profit: ${profit:.2f}")

# Print the trades
print("Trades:")
for trade in trades:
    print(f"Date: {trade['Date'].date()} | Action: {trade['Action']} | Price: ${trade['Price']:.2f} | Profit: ${trade['Profit']:.2f}")

# Print the probability of a positive trade
print(f"Probability of positive trade: {probability:.2f}%")

# %% [markdown]
# # Scanning The Market
# Instead of testing stocks one-by-one, a more efficient way would to enter your prefered probability and get a list of stocks that fit the parameters.

# %%
Probability = []
# function that attempts to calc_prob but returns 0 if divby0 err
def try_prob(stock_symbol):
    try:
        j = calculate_profit(stock_symbol)[2]
        Probability.append(j)
    except:
        Probability.append(0)

# looping through the list of stocks
for i in stocks['Symbol']:
    try_prob(i)

# %%
# appending list to dataset
stocks['Probability'] = Probability

# Calculate the frequency of each value
value_counts = {}
for value in Probability:
    value_counts[value] = value_counts.get(value, 0) + 1

# Extract the values and frequencies
values = list(value_counts.keys())
frequencies = list(value_counts.values())

# Create the bar chart
fig = go.Figure(data=[go.Bar(x=values, y=frequencies)])

# Update layout if needed
fig.update_layout(
    title="Stock Probability Distribution",
    xaxis_title="Probability",
    yaxis_title="Frequencies"
)

# dark mode B)
fig.layout.template = 'plotly_dark'

# Show the plot
fig.show()

# %% [markdown]
# Why is the distribution important? 
# 
# It helps give us an idea of what is considered a "high" or "low" probability. Prior to making the distribution, I would search for stocks that had a probability of 90% which I now see is wildly unrealistic.

# %%
# input desired probability
desired_probability = prob 

# empty list
selected_stocks = []

# finding stocks that have the desired probability
for index, row in stocks.iterrows():
    if desired_probability <= row[11]:
        selected_stocks.append(row[0])
        
print("Your selected stocks:")
for i in selected_stocks:
    print(i)


