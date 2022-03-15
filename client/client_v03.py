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
# from config.config import *
import time

import MetaTrader5 as mt5

os.system('cls')
print("Client")
host = "localhost"
port = 8090
print(host,port)
debug = True

url = f"http://{host}:{port}"
print("Try to get Connection : "+url)
r = requests.get(url)
print(r.text)

name = input('Enter Symbol Name : ')
timeframe = "M1"
num_bars= 200
signal = 0
count = 0
triger_signal_init = 0
lot = input("Taille Lots :  ")
comment = f'Ichimoku_{timeframe}'
cs = Console()

def open_trade_buy(action, symbol, lot, deviation, comment):
    '''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
    '''
    # prepare the buy request structure
    mt5.initialize()
    symbol_info = mt5.symbol_info(symbol)
    ea_magic_number = 9986989
    if action == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif action =='sell':
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point

    buy_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": trade_type,
        "price": price,
        # "sl": price - sl_points * point,
        # "tp": price + tp_points * point,
        "deviation": deviation,
        "magic": ea_magic_number,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    # send a trading request
    result = mt5.order_send(buy_request)
    mt5.shutdown()        
    return result, buy_request

while count < 100:
	triger_signal = 0
	route_data = f"{url}/ichimoku/{name}/{timeframe}/{num_bars}"
	r2 = requests.get(route_data)
	data = json.loads(r2.text)
	df = pd.DataFrame(data)
	print(data)
	full_df = df.copy()
	print(full_df)
	last_df = df.tail(1)
	last_signal = last_df['Strategy'][-1]

	print()
	rsi = full_df.T['RSI 7P']
	rsi = rsi.T[name]
	print(rsi)

	print()
	print("-"*20,signal,"-"*20)
	# print(f"Last_Message_{signal}\t:\n{last_df}")
	print(f"Last Signal_{signal}\t: {last_signal}")

	triger_signal_name = None
	if str(last_signal) == 'buy':
		triger_signal_name = "buy"
		triger_signal = 1
	if str(last_df) == 'sell':
		triger_signal_name = "sell"
		triger_signal = -1
	
	compart_triger = f"Triger_ini | triger_signal \t:\t{triger_signal_init}|{triger_signal} "
	print(compart_triger)
	if triger_signal_init == triger_signal:
		cs.print("Une Action est en Court",justify='center',style='magenta')
		if rsi < 30:
			open_trade_buy(action = triger_signal_name, symbol=name, lot=lot, deviation=20, comment=comment)

		if rsi > 70:
			open_trade_buy(action = triger_signal_name, symbol=name, lot=lot, deviation=20, comment=comment)

	if triger_signal_init != triger_signal:
		print(f"Triger_ini != triger_signal \t:\t{triger_signal_init}|{triger_signal} ")
		cs.print("Action Possible",justify='center',style='cyan')
		open_trade_buy(action = triger_signal_name, symbol=name, lot=lot, deviation=20, comment=comment)
		triger_signal_init = triger_signal
		
	print(f"Triger\t:\t{triger_signal}")
	signal += 1

	time.sleep(1)