#!/usr/bin/env python
# coding: utf-8

# # 10 Day Moving Average Stock Picker

# The purpose of this notebook is to scan the stock market for stock that have a certain probability of returning a positive profit trading above the 10 day moving average. Instead of using the entire market, this dataset has the top 600 publicly listed companies by market cap.

# In[1]:


# importing packages
import yfinance as yf
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

# importing list of stocks
stocks = pd.read_csv('List of Stocks.csv')
stocks


# # Your Parameters
# This program is set up to return stocks that make a specific probability of positive returns trading above the 10 day moving average. This program is dependent on 2 main parameters, plus one optional:
# 
# "past days" the amount of the days into the past. For example, putting 365 would give you info on the past year. 
# 
# "prob" is your desired probability as a percent. 
# 
# "tick" shows you an individual stock's price history, 10 day moving average, and probability of positive profit over the 10DMA

# In[19]:


# enter your prefered timeframe in days in the parenthesis:
past_days = (90)

# enter your prefered probability of a positive profit:
prob = (50)

# ticker for individual stock
tick = 'AMZN'


# In[4]:


# Setting time periods: today, one year ago
current_date = dt.datetime.now() - dt.timedelta(days=1)
one_ya = current_date - dt.timedelta(days=past_days+10) # add 10 days to whatever period to makeup for delay in moving average

# formatting
time_n = current_date.strftime("%Y-%m-%d")
time_nm1 = one_ya.strftime("%Y-%m-%d")


# In[17]:


# fuction that returns probability of return

def calc_prob(ticker_symbol):
    # defining start and end dates
    start_date = time_nm1
    end_date = time_n
    
    # getting historal price data
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    
    # calculating the 1- day moving average
    data['10DMA'] = data['Close'].rolling(window=10).mean()
    
    # set probability variables
    total_trades = 0
    profit_trades = 0
    
    # iterate to find crosses over the MA
    for i in range(1, len(data)):
        current_close = data['Close'].iloc[i]
        prev_close = data['Close'].iloc[i - 1]
        current_ma = data['10DMA'].iloc[i]
        prev_ma = data['10DMA'].iloc[i - 1]
        
        if prev_close < prev_ma and current_close > current_ma:
            total_trades += 1
            profit = current_close - prev_close
            if profit > 0:
                profit_trades =+ 1
        
    probability = (profit_trades/total_trades)*100
    
    return probability


# # Testing Individual Stocks
# Below shows a function that returns a chart of the price history with the 10 day moving average. Underneath, it shows the % probability of returning a positive profit at the specified timeframe. 

# In[20]:


# enter ticker symbol in the quotes

enter_stock = tick # enter stock choice here

# setting up the data
stock_data = yf.download(enter_stock, start=time_nm1, end=time_n)
stock_data['10DMA'] = stock_data['Close'].rolling(window=10).mean()
stock_data = stock_data.dropna()

# showing the price history and DMA
fig = px.line(
                 stock_data, 
                 y="Close", 
                 title=enter_stock, 
                 color_discrete_sequence=['red','blue']
                 )

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

print("------------------------------------------------------------------------------------")
print("Probability of profit for " + enter_stock + " is " + str(calc_prob(enter_stock)) + "%")


# # Scanning The Market
# Instead of testing stocks one-by-one, a more efficient way would to enter your prefered probability and get a list of stocks that fit the parameters.

# In[21]:


# making a column for each stock's respective probability
Probability = []
for i in stocks['Symbol']:
    try:
        j = calc_prob(i)
        Probability.append(j)
    except:
        Probability.append(0)


# In[22]:


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

# Show the plot
fig.show()


# Why is the distribution important? 
# 
# It helps give us an idea of what is considered a "high" or "low" probability. Prior to making the distribution, I would search for stocks that had a probability of 90% which I now see is wildly unrealistic.

# In[23]:


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

