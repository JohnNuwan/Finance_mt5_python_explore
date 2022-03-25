

import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt
from binance.client import Client
from statistics import mean
import os
import sys 

from rich import print
from rich.console import Console
from rich.style import Style
import pandas as pd 
import numpy as np
from datetime import datetime 
import requests
import json

import time

import schedule

from pandas_datareader import data, wb
import datetime
# plt.rcParams['figure.figsize'] = [12, 7]
# plt.rc('font', size=14)



host = "localhost"
port = 8090
debug = True

url = f"http://{host}:{port}"
os.system('cls')
cs = Console()
cs.log("Client")
cs.log(host,port)


cs.log("Try to get Connection : "+url)
r = requests.get(url)
cs.log(r.text)
name = "GOLD"#input('Enter Symbol Name :')
timeframe = "M1"
num_bars= 200
signal = 0
count = 0
triger_signal_init = 0
lot = 0.02	
comment = f'Ichimoku_{timeframe}'

def get_data():
    route_data = f"{url}/OHLC/{name}/{timeframe}/{num_bars}"
    r2 = requests.get(route_data)
    data = json.loads(r2.text)
    df = pd.read_json(data)
    # df = df['close']


    df['prev_close'] = df.close.shift(1)
    df["Candle way"] = -1
    df['mean_prev_close'] = df.close.rolling(window=21,center=True).max()

    df['Up_Down'] = np.NaN
    df['Up_Down'] = np.where((df['prev_close'] < df['close']), 1, df['Up_Down'])
    df['Up_Down'] =  np.where((df['prev_close'] > df['close']), -1, df['Up_Down'])
    df["amplitude"] = np.abs(df["close"] - df["open"])

    # Support and resistance building
    df["support"] = np.nan
    df["resistance"] = np.nan

    df.loc[(df["low"].shift(3) > df["low"].shift(2)) &
        (df["low"].shift(2) > df["low"].shift(1)) &
        (df["low"].shift(1) > df["low"].shift(0)), "support"] = df["low"]


    df.loc[(df["high"].shift(3) < df["high"].shift(2)) &
    (df["high"].shift(2) < df["high"].shift(1)) &
    (df["high"].shift(1) < df["high"].shift(0)), "resistance"] = df["high"]


    # Create Simple moving average 30 days
    df["SMA fast"] = df["close"].rolling(30).mean()

    # Create Simple moving average 60 days
    df["SMA slow"] = df["close"].rolling(60).mean()
    df["smooth resistance"] = df["resistance"].fillna(method="ffill")
    df["smooth support"] = df["support"].fillna(method="ffill")

    df["mean smooth"] = (df["smooth resistance"] + df["smooth support"])/2

    return df


import numpy as np
import matplotlib.pyplot as plt

print("Plot")

fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111)
plt.ion()

fig.show()
fig.canvas.draw()

for i in range(0,100):
    ax.clear()
    df = get_data()

    ax.plot(df.close)
    ax.plot(df['mean smooth'].shift(9))
    ax.plot(df['smooth support'].shift(9))
    ax.plot(df['SMA slow'].shift(9))
    
    fig.canvas.draw()
    plt.show()