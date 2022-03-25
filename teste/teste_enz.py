

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
num_bars= 2000
signal = 0
count = 0
triger_signal_init = 0
lot = 0.04 
comment = f'Ichimoku_{timeframe}'

TOKEN = "1801058128:AAETqJbJMjVUt6ewpjYL2ZVIU8wzIlrzJL4"
CHAT_ID = "@Forex_free_perfect"

# Type = 0
# route_open_position = f"/open_position/{name}/{timeframe}/{Type}/{comment}/{lot}"

def message(symbol,ut,Type,price):
    time_now = datetime.datetime.now()
    MESSAGE = f"symbol : {symbol} ,\n\n Zone De Recherche {Type}\n\n At Price : {price}\n\ntime = {time_now}\nUT : {ut}\n\n\t Strat : Ichimoku_{ut}"
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE}')
    print(r.status_code)



def ichi(name,timeframe,num_bars):
    route_data = f"{url}/OHLC/{name}/{timeframe}/{num_bars}"
    r2 = requests.get(route_data)
    data = json.loads(r2.text)
    df = pd.read_json(data)


    nine_periodf_high = df['high'].rolling(window= 9).max()
    nine_periodf_low = df['low'].rolling(window= 9).min()

    periodf26_high = df['high'].rolling(window=26).max()
    periodf26_low = df['low'].rolling(window=26).min()


    df['tenkan_sen'] = (nine_periodf_high + nine_periodf_low) /2

    # Kijun-sen (Base Line): (26-periodf high + 26-periodf low)/2))
    df['kijun_sen'] = (periodf26_high + periodf26_low) / 2
    df['prev_kijun_sen'] = df['kijun_sen'].shift(1)
    df['prev_tenkan_sen'] = df['tenkan_sen'].shift(1)

    # Senkou Span A (Leadfing Span A): (Conversion Line + Base Line)/2))
    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    # Senkou Span B (Leadfing Span B): (52-periodf high + 52-periodf low)/2))
    periodf52_high = df['high'].rolling(window=52).max()
    periodf52_low = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((periodf52_high + periodf52_low) / 2).shift(52)

    d = df.copy()
    d['chikou_span'] = d['close'].shift(-26)
    # d.dropna(inplace=True)
    d['above_cloud'] = 0
    d['above_cloud'] = np.where((d['low'] > d['senkou_span_a'])  & (d['low'] > d['senkou_span_b'] ), 1, d['above_cloud'])
    d['above_cloud'] = np.where((d['high'] < d['senkou_span_a']) & (d['high'] < d['senkou_span_b']), -1, d['above_cloud'])
    d['A_above_B'] = np.where((d['senkou_span_a'] > d['senkou_span_b']), 1, -1)
    d['tenkan_kiju_cross'] = np.NaN
    d['tenkan_kiju_cross'] = np.where((d['tenkan_sen'].shift(1) <= d['kijun_sen'].shift(1)) & (d['tenkan_sen'] > d['kijun_sen']), 1, d['tenkan_kiju_cross'])
    d['tenkan_kiju_cross'] = np.where((d['tenkan_sen'].shift(1) >= d['kijun_sen'].shift(1)) & (d['tenkan_sen'] < d['kijun_sen']), -1, d['tenkan_kiju_cross'])
    d['price_tenkan_cross'] = np.NaN
    d['price_tenkan_cross'] = np.where((d['open'].shift(1) <= d['tenkan_sen'].shift(1)) & (d['open'] > d['tenkan_sen']), 1, d['price_tenkan_cross'])
    d['price_tenkan_cross'] = np.where((d['open'].shift(1) >= d['tenkan_sen'].shift(1)) & (d['open'] < d['tenkan_sen']), -1, d['price_tenkan_cross'])
    d['buy'] = np.NaN
    d['buy'] = np.where((d['above_cloud'].shift(1) == 1) & (d['A_above_B'].shift(1) == 1) & ((d['tenkan_kiju_cross'].shift(1) == 1) | (d['price_tenkan_cross'].shift(1) == 1)), 1, d['buy'])
    d['buy'] = np.where(d['tenkan_kiju_cross'].shift(1) == -1, 0, d['buy'])
    # d['buy'].ffill(inplace=True)

    d['sell'] = np.NaN
    d['sell'] = np.where((d['above_cloud'].shift(1) == -1) & (d['A_above_B'].shift(1) == -1) & ((d['tenkan_kiju_cross'].shift(1) == -1) | (d['price_tenkan_cross'].shift(1) == -1)), -1, d['sell'])
    d['sell'] = np.where(d['tenkan_kiju_cross'].shift(1) == 1, 0, d['sell'])
    # d['sell'].ffill(inplace=True)
    d['position'] = d['buy'] + d['sell']
    d['stock_returns'] = np.log(d['open']) - np.log(d['open'].shift(1))
    d['strategy_returns'] = d['stock_returns'] * d['position']
    # d[['stock_returns','strategy_returns']].cumsum().plot(figsize=(15,8))

    # print(d.tail(2))

    data  = d.fillna(0, inplace=False)
    return data

count =0
while True:
    data = ichi(name,"M1",num_bars)
    print(data.tail(1))
    last_buy = data['buy'][-1]
    last_sell = data['sell'][-1]
    price = data['close'][-1]
    print('-'*10)
    print(f' last_buy : {last_buy} | last_sell : {last_sell}')

    if last_sell == 0.0 or last_buy == 0.0:
        print()
        print("Nothing")

    if last_sell == 1:
        print("Sell Time ")
        message(symbol=name,ut='M1',Type="Sell",price=price)
        route_data = f"{url}/open_position/{name}/M1/sell/{comment}/{lot}"
        r2 = requests.get(route_data)
        data = json.loads(r2.text)
        # df = pd.read_json(data)

    if last_buy == 1:
        print("Buy Time ")
        message(symbol=name,ut='M1',Type="Buy",price=price)
        route_data = f"{url}/open_position/{name}/M1/buy/{comment}/{lot}"
        r2 = requests.get(route_data)
        data = json.loads(r2.text)


    time.sleep(60)
    count+=1
# if df['buy'][-1] is not Nan:
#     print("Signale")

# if df['buy'][-1] is None:
#     print("Signale Nan")