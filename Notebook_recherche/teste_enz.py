

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
lot = 0.02
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

def calc_dif(df):
    """
    CALCUL D'UNE DIFFÉRENCE EN POURCENTAGE

    Augmenter ou diminuer un montant de 1% signifie augmenter ou diminuer ce montant d'une certaine proportion.
    Les pourcentages sont calculés sur une base de 100, c'est pourquoi on parle de pourCENTage.
    (Il existe également d'autres bases de calcul, comme une base de 24 pour un jour ou une base de 60 pour une heure ou une minute.)
    Pour augmenter ou diminuer un montant de 1%, il faut définir :
    V1 : la valeur de départ, soit le montant de base que l'on veut augmenter ou diminuer ;
    V2 : la valeur finale, soit le nouveau montant après l'augmentation ou la diminution.
    La formule pour calculer le pourcentage de l'augmentation ou de la diminution est :
    Différence (en %) = ((V2 - V1) / V1) x 100 
    """
    V2   = df.price_current
    V1   = df.price_open
    Diff = 0
    if df.type == 0: 
        Diff = ((V2 - V1 )/V1)*100
        # print("Chang\t:",Diff, "%")
        return Diff

    if df.type == 1: 
        Diff = ((V1 - V2 )/V2)*100
        # print("Chang\t:",Diff, "%")
        return Diff


def pips(df):

    if str(df.price_open).index('.') >= 3:  # JPY pair
        multiplier = 0.001
    else:
        multiplier = 0.0001

    pips = round((df.price_current - df.price_open) / multiplier)
    return int(pips)


def chek_take_position(symbol,comment,Type):
    url = f"http://{host}:{port}"
    try:
        route_position = "/positions_en_court"
        url = f"{url}{route_position}"
        cs.log(url)
        count = 0
        volume_count = 0

        tt_pips = 0
        profit = 0
        tt_change = 0
        itme_now = datetime.now()
        recv_data = requests.get(url)
        encode_data = json.loads(recv_data.text)
        # cs.log(encode_data)
        df = pd.read_json(encode_data)
        list_frame = []

        df.drop(columns=['external_id','time_msc', 'reason','time_update','time_update_msc'],inplace=True)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index(df['time'],inplace=True)
        df["pct_chang"] =  df.apply(lambda row: calc_dif(row),axis=1)
        df["Pips"] =  df.apply(lambda row: pips(row),axis=1)

        print(df)
        # symbol_df_filtre = pd.DataFrame()

        for row in df.itertuples():
            # print(f"{row.symbol}      {row.type}      {row.comment}      {row.profit}      {row.volume}")
            if row.symbol == symbol:#
                # print(row)
                if row.comment == comment:
                    if row.type == Type:
                        volume_count += row.volume
                        profit += row.profit
                        tt_change += row.pct_chang
                        tt_pips += row.Pips
                        print(f"{row.symbol} {row.type} {row.ticket} Changement\t:\t",calc_dif(row))
                        # print(pips(row))
                        # data_symbol = {
                        #       "Time" : row.time,#pd.to_datetime(row.time, unit='s'),

                        #       "Name" : row.symbol,
                        #       "Id_ticker" : row.identifier,
                        #       "Profit" :row.profit,
                        #       "Lot" : row.volume,
                        #       "Comment" : row.comment,
                        #       'Type' : row.type
                        #       }
                        # print(data_symbol)
                        count +=1

        data_send = {
                "Name": symbol,
                "Type":Type,
                "Total":count,
                'TT_Volume': volume_count,
                "profit": profit,
                "TT_Change": tt_change,
                "TT_Pips" : tt_pips
        }
        return data_send
                    # # last_time = row.index
                    # data_check = {
                    #       "time" : row.time,
                    #       "Name": symbol,
                    #       "Nb Pos" : count,
                    #       "Lot" : volume_count,
                    #       "Type" : Type
                    #   }
                    # # df = pd.DataFrame(data_check)
                    # print(data_check)
                    # return data_check#df.to_json()
            
            # else :
                # return "Note Data"
    except Exception as e:
        return e




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

def worker():
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

    


        if last_sell == -1:
            Type = 1
        
            verif = chek_take_position(symbol=name,comment=comment,Type=Type)
            if verif['Total'] < 1 or verif['Total'] == 0: 
                print("Sell Time ")
                message(symbol=name,ut='M1',Type="Sell",price=price)
                route_data = f"{url}/open_position/{name}/M1/sell/{comment}/{lot}"
                r2 = requests.get(route_data)
                data = json.loads(r2.text)
                # df = pd.read_json(data)

        if last_buy == 1:
            Type = 0
        
            verif = chek_take_position(symbol=name,comment=comment,Type=Type)
            if verif['Total'] < 1 or verif['Total'] == 0: 
                print("Buy Time ")
                message(symbol=name,ut='M1',Type="Buy",price=price)
                route_data = f"{url}/open_position/{name}/M1/buy/{comment}/{lot}"
                r2 = requests.get(route_data)
                data = json.loads(r2.text)


    # time.sleep(60)
    # count+=1
# if df['buy'][-1] is not Nan:
#     print("Signale")

# if df['buy'][-1] is None:
#     print("Signale Nan")

schedule.every(1).minutes.do(worker)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print(e)