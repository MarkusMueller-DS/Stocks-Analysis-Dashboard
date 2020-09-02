# imports
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from datetime import datetime
import yfinance as yf

import matplotlib.pyplot as plt
from matplotlib import gridspec

from PIL import Image

import streamlit as st

# show image
image = Image.open('image.jpg')
st.image(image, use_column_width=True)


# Write a title
st.title('Stock Dashboard')

# text input to get the ticker symbol of the share
ticker_symbol = st.text_input('Ticker symbol of the share:', value='FB')
st.write('The dashboard will be created for the following ticker symbol:', ticker_symbol)

# date input for start and end date
start_date = st.date_input('Start date:')
st.write('You selected:', start_date)

end_date = st.date_input('End date:', max_value=datetime.today())
st.write('You selected', end_date)

# get the price of the share and save it into a DataFrame 
df = yf.download(ticker_symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), progress=False)

# choose indicators
indicators = st.multiselect('Choose your indicators', ['Volume', 'RSI', 'MACD', 'MFI'])

# display indicators to the user
if len(indicators) == 1:
    st.text(f'You selected: {indicators[0]}')
elif len(indicators) == 2:
    st.text(f'You selected: {indicators[0]}, {indicators[1]}')
elif len(indicators) == 3:
    st.text(f'You selected: {indicators[0]}, {indicators[1]}, {indicators[2]}')
elif len(indicators) == 4:
    st.text(f'You selected: {indicators[0]}, {indicators[1]}, {indicators[2]}, {indicators[3]}')
else:
    st.text('Plese select an indicator')

###################################
# define plots

# Price
def Price():
    # ax1 needs to be global since other functions are using it 
    global ax1 
    ax1 = plt.subplot(gs[0])
    ax1.plot(df.index, df['Adj Close'])
    ax1.fill_between(df.index, df['upper_Boll'], df['lower_Boll'], color='grey',  alpha=0.5)
    ax1.plot(df.index, df['SMA_Boll'], alpha=0.5)
    plt.ylabel('Price')
    ax1.set_title(f'{ticker_symbol} Stock Analysis')

# Volume
def Volume(axis_pos):
    axis_pos.bar(df.index, df['Volume'])
    plt.ylabel('Volume')
    
# RSI
def Rsi(axis_pos):
    axis_pos.plot(df.index, df['RSI'])
    plt.axhline(30, linestyle='--', lw=1, alpha=0.5, color='red')
    plt.axhline(70, linestyle='--', lw=1, alpha=0.5, color='red')
    plt.ylabel('RSI')
    
# MACD
def Macd(axis_pos):
    axis_pos.plot(df.index, df['MACD'])
    axis_pos.plot(df.index, df['MACD_signal'])
    plt.ylabel('MACD')
    
# MFI
def Mfi(axis_pos):
    axis_pos.plot(df.index, df['MFI'])
    plt.axhline(20, linestyle='--', lw=1, alpha=0.5, color='red')
    plt.axhline(80, linestyle='--', lw=1, alpha=0.5, color='red')
    plt.ylabel('MFI')
    
    
plot_indicator_dict = {'Volume': Volume, 'RSI': Rsi, 'MACD': Macd, 'MFI': Mfi}

###################################
# Calculate indicators

## RSI
delta = df['Adj Close'].diff()
delta.dropna(inplace=True)
up = delta.copy()
up[up < 0] = 0
down = delta.copy()
down[down > 0] = 0
AVG_gain = up.rolling(window=14).mean()
AVG_loss = abs(down.rolling(window=14).mean())
RS = AVG_gain / AVG_loss
RSI = 100.0 - (100.0 / (1.0 + RS))
df['RSI'] = RSI

## MACD
ema_12 = df['Adj Close'].ewm(span=12, adjust=False).mean()
ema_26 = df['Adj Close'].ewm(span=26, adjust=False).mean()
MACD = ema_12 - ema_26
signal_line = MACD.ewm(span=9, adjust=False).mean()
df['MACD'] = MACD
df['MACD_signal'] = signal_line

## Bollinger Band
df['SMA_Boll'] = df['Adj Close'].rolling(window=20).mean()
df['std_Boll'] = df['Adj Close'].rolling(window=20).std()
df['upper_Boll'] = df['SMA_Boll'] + (df['std_Boll'] * 2)
df['lower_Boll'] = df['SMA_Boll'] - (df['std_Boll'] * 2)

## Money Flow Index (MFI)
df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
df['money_flow'] = df['typical_price'] * df['Volume']
df['diff'] = df['typical_price'].diff(1)
df['positive_money_flow'] = np.where(df['diff'] > 0, df['money_flow'], 0)
df['negative_money_flow'] = np.where(df['diff'] < 0, df['money_flow'], 0)
df['positive_money_flow_p'] = df['positive_money_flow'].rolling(window=14).sum()
df['negative_money_flow_p'] = df['negative_money_flow'].rolling(window=14).sum()
df['money_flow_ration'] = df['positive_money_flow_p'] / df['negative_money_flow_p']
df['MFI'] = 100 - 100/(1 + df['money_flow_ration'])

##################################
# Define plot
plt.style.use('fivethirtyeight')
    
# drop rows with NaNs in RSI column
#df.dropna(inplace=True)
    
# check interactive sizing from choosen indcators 

if len(indicators) == 1:
    n_cols = 2
    hight_ratio = [2,1]
    size = (12,5)
    fig = plt.figure(figsize=size)
    gs = gridspec.GridSpec(n_cols, 1, height_ratios=hight_ratio)
    Price()
    
    ax2 = plt.subplot(gs[1], sharex = ax1)
    plot_indicator_dict[indicators[0]](ax2)
    
    plt.setp(ax1.get_xticklabels(), visible=False)
    
elif len(indicators) == 2:
    n_cols = 3
    hight_ratio = [2,1,1]
    size = (12,6)
    fig = plt.figure(figsize=size)
    gs = gridspec.GridSpec(n_cols, 1, height_ratios=hight_ratio)
    Price()
    
    ax2 = plt.subplot(gs[1], sharex = ax1)
    plot_indicator_dict[indicators[0]](ax2)
    
    ax3 = plt.subplot(gs[2], sharex = ax1)
    plot_indicator_dict[indicators[1]](ax3)
    
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    
elif len(indicators) == 3:
    n_cols = 4
    hight_ratio = [2,1,1,1]
    size = (12,8)
    fig = plt.figure(figsize=size)
    gs = gridspec.GridSpec(n_cols, 1, height_ratios=hight_ratio)
    Price()
    
    ax2 = plt.subplot(gs[1], sharex = ax1)
    plot_indicator_dict[indicators[0]](ax2)
    
    ax3 = plt.subplot(gs[2], sharex = ax1)
    plot_indicator_dict[indicators[1]](ax3)
    
    ax4 = plt.subplot(gs[3], sharex = ax1)
    plot_indicator_dict[indicators[2]](ax4)
    
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax3.get_xticklabels(), visible=False)
    
elif len(indicators) == 4:
    n_cols = 5
    hight_ratio = [2,1,1,1,1]
    size = (12,10)
    fig = plt.figure(figsize=size)
    gs = gridspec.GridSpec(n_cols, 1, height_ratios=hight_ratio)
    Price()
    
    ax2 = plt.subplot(gs[1], sharex = ax1)
    plot_indicator_dict[indicators[0]](ax2)
    
    ax3 = plt.subplot(gs[2], sharex = ax1)
    plot_indicator_dict[indicators[1]](ax3)
    
    ax4 = plt.subplot(gs[3], sharex = ax1)
    plot_indicator_dict[indicators[2]](ax4)
    
    ax5 = plt.subplot(gs[4], sharex = ax1)
    plot_indicator_dict[indicators[3]](ax5)
    
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax4.get_xticklabels(), visible=False)

else:
    fig, ax = plt.subplots(figsize=(12,4))
    ax.plot(df.index, df['Adj Close'])
    ax.set_ylabel('Price')
    fig.suptitle(f'{ticker_symbol} Stock Analysis')

st.pyplot()