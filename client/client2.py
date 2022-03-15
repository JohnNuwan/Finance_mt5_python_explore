import os
import sys 
from rich.console import Console
import MetaTrader5 as mt5
from rich import print
from datetime import datetime 

import requests
import json

import time
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

name = "BTCUSD"
timeframe = "M1"
comment = f'Ichimoku_{timeframe}'

num_bars= 200
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
count = 0

open_trade_buy(action="sell", symbol=name, lot=0.02, deviation=20, comment=comment)
while count < 5:
	route_data = f"{url}/positions_en_court/{name}"
	r2 = requests.get(route_data)
	data = json.loads(r2.text)
	# df = pd.read_json(data)
	# print(df.tail())
	print(data)
	count +=1
	time.sleep(2)