from rich.table import Table

import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt

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
from scipy.stats import linregress
import datetime
# plt.rcParams['figure.figsize'] = [12, 7]
# plt.rc('font', size=14)
import warnings

import ta

warnings.simplefilter('ignore', FutureWarning)

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
num_bars= 500   
signal = 0
count = 0
triger_signal_init = 0
lot = 0.04 
comment = f'Engulfin_{timeframe}'

TOKEN = "1801058128:AAETqJbJMjVUt6ewpjYL2ZVIU8wzIlrzJL4"
CHAT_ID = "@Forex_free_perfect"


table = Table(title=f"Name : {name} ut : {timeframe}")

table.add_column("Datetime", justify="right", style="cyan", no_wrap=True)
table.add_column("Up Down", style="magenta")




# Type = 0
# route_open_position = f"/open_position/{name}/{timeframe}/{Type}/{comment}/{lot}"

def message(symbol,ut,Type,price):
    time_now = datetime.datetime.now()
    MESSAGE = f"symbol : {symbol} ,\n\n Zone De Recherche {Type}\n\n At Price : {price}\n\ntime = {time_now}\nUT : {ut}\n\n\t Strat : Ichimoku_{ut}"
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE}')
    print(r.status_code)

def engulfing(df):

    
    df["Candle way"] = -1
    df.loc[(df["open"] - df["close"]) < 0, "Candle way"] = 1
    df["amplitude"] = np.abs(df["close"] - df["open"])
    
    
    buy =(df["Candle way"].shift(3).iloc[-1] == -1) and\
        (df["Candle way"].shift(2).iloc[-1] == -1) and\
        (df["Candle way"].shift(1).iloc[-1] == -1) and\
        (df["Candle way"].iloc[-1] == 1) and\
        (df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
        (df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
        (df["amplitude"].shift(1).iloc[-1]*1.5 < df["amplitude"].iloc[-1])
    
    
    
    sell = (df["Candle way"].shift(3).iloc[-1] == 1) and\
       (df["Candle way"].shift(2).iloc[-1] == 1) and\
       (df["Candle way"].shift(1).iloc[-1] == 1) and\
       (df["Candle way"].iloc[-1] == -1) and\
       (df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
       (df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
       (df["amplitude"].shift(1).iloc[-1] * 1.5< df["amplitude"].iloc[-1])
    

    return {"Buy":buy, "Sell":sell}

def Strat(name,timeframe,num_bars):
    route_data = f"{url}/OHLC/{name}/{timeframe}/{num_bars}"
    r2 = requests.get(route_data)
    data = json.loads(r2.text)
    df = pd.read_json(data)
    df.drop(columns=['spread','real_volume'],inplace=True)
    # df = df['close']

    df['prev_close'] = df.close.shift(1)
    df["Candle way"] = -1
    # df['mean_prev_close'] = df.close.rolling(window=21,center=True).max()

    df['Up_Down'] = np.NaN
    df['Up_Down'] = np.where((df['prev_close'] < df['close']), 1, df['Up_Down'])
    df['Up_Down'] =  np.where((df['prev_close'] > df['close']), -1, df['Up_Down'])
    df["amplitude"] = np.abs(df["close"] - df["open"])

     # Support and resistance building
    df["support"] = np.nan
    df["resistance"] = np.nan

    df.loc[(df["low"].shift(5) > df["low"].shift(4)) &
        (df["low"].shift(4) > df["low"].shift(3)) &
        (df["low"].shift(3) > df["low"].shift(2)) &
        (df["low"].shift(2) > df["low"].shift(1)) &
        (df["low"].shift(1) > df["low"].shift(0)), "support"] = df["low"]


    df.loc[(df["high"].shift(5) < df["high"].shift(4)) &
    (df["high"].shift(4) < df["high"].shift(3)) &
    (df["high"].shift(3) < df["high"].shift(2)) &
    (df["high"].shift(2) < df["high"].shift(1)) &
    (df["high"].shift(1) < df["high"].shift(0)), "resistance"] = df["high"]


    # Create Simple moving average 30 days
    df["SMA fast"] = df["close"].rolling(30).mean()

    # Create Simple moving average 60 days
    df["SMA slow"] = df["close"].rolling(60).mean()

    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=7).rsi()

    # RSI yersteday
    df["rsi yersteday"] = df["rsi"].shift(1)

    # Create the signal
    df["signal"] = 0

    df["smooth resistance"] = df["resistance"].fillna(method="ffill")
    df["smooth support"] = df["support"].fillna(method="ffill")
    df["amplitude H/L"] = np.abs(df["high"] - df["low"])

    # df['Up_Down_stat'] = df.Up_Down.rolling(window=21).mean().pct_change() 



    if df['Up_Down'][-1] == 1:
        cs.print("Up",justify='center', style='green')
        # table.add_row(name, "Up", style="green")
    if df['Up_Down'][-1] == -1:
        cs.print("Down",justify='center', style='red')
        # table.add_row(name, "Down", style="red")

    if df['Up_Down'][-1] < 1 and df['Up_Down'][-1] > -1 :
        cs.print("Flat",justify='center', style='red')
    
    recv_data = engulfing(df)

    if recv_data['Buy'] or recv_data['Sell'] == True:
        print("Candel")
        if recv_data["Buy"] == True:
            route_data = f"{url}/open_position/{name}/M1/buy/{comment}/{lot}"
            r2 = requests.get(route_data)
        
        if recv_data["Sell"] == True:
            route_data = f"{url}/open_position/{name}/M1/sell/{comment}/{lot}"
            r2 = requests.get(route_data)

        # sys.exit()

    else:
        print(recv_data)
       
    print(df.tail()) 
    return df


count = 0




while count < 10000:
    os.system('cls')
    print("\n","-"*15,"Count : ",count,"-"*15)
    Strat(name,timeframe,num_bars)
    # cs.print(table)

    time.sleep(10)
    count +=1
