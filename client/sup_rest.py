# /sup_res/{name}/{timeframe}/{num_bars}
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


import time

import schedule




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

name = "XAUUSD"#input('Enter Symbol Name : ')
timeframe = "M1"
num_bars= 200
signal = 0
count = 0
triger_signal_init = 0
# lot = input("Taille Lots :  ")
comment = f'Support_Ress'
cs = Console()




TOKEN = "1801058128:AAETqJbJMjVUt6ewpjYL2ZVIU8wzIlrzJL4"
# CHAT_ID = "@sup_res_perfect_mtf"
CHAT_ID = "@Scalp_Perfect"		

list_data = ["XAUUSD",'GER40.cash',"BTCUSD"]
list_ut = ["M1","M3",'M5',"M15"]

def worker(name,timeframe):
	
	triger_signal = 0
	route_data = f"/sup_res/{name}/{timeframe}/{num_bars}"
	r2 = requests.get(url+route_data)
	data = json.loads(r2.text)
	df = pd.read_json(data)
	# print(data)
	full_df = df.copy()
	# print(full_df.tail(1))
	price = full_df['close'][-1]

	last_rsi = full_df['rsi'][-1]
	prev_rsi = full_df['rsi yersteday'][-1]

	last_sma_fast = full_df["SMA fast"][-1]
	last_sma_slow = full_df["SMA slow"][-1]

	last_res = full_df["smooth resistance"][-1]
	last_supp = full_df["smooth support"][-1]
	last_signal = full_df["signal"][-1]

	time_data = full_df.index[-1]

	data = {
			"time" : time_data,
			"name" : name,
			"timeframe" : timeframe,
			"Last resistance" : last_res,
			"Last support" : last_supp,
			"Last Price" : price,
			"Last RSI 7P" : last_rsi,
			"Prev RSI 7P" : prev_rsi,
			"SMA fast 10P" : last_sma_fast,
			"SMA slow 21P" : last_sma_slow,
			"Last_Signal" : last_signal,
	}

	return data

	# if last_signal == 1 or last_signal == -1:
	# 	triger_signal_sup = last_signal
	# 	print(triger_signal_sup)
	# 	print()
	# 	print(data)
	# 	time_now = datetime.now()
	# 	MESSAGE = f"symbol : {name} ,\n\nprice : {price} ,\n\nZone De Resistance : {last_res}\n\nZone De Support : {last_supp}\n\ntime : {time_now}\n\nUT : {timeframe}\n\n Signal : {last_signal}\n\n\t Strat : {comment}"
	# 	# print((MESSAGE))


def job(name):
	count = 0
	for timeframe in list_ut:		
		process = worker(name,timeframe)
		p_signal = process['Last_Signal']

		if p_signal != 0:
			print("action",p_signal,timeframe,name)
			route_data = f"{url}/ichimoku/{name}/{timeframe}/{num_bars}"
			r2 = requests.get(route_data)
			data = json.loads(r2.text)
			df = pd.DataFrame(data)
			# M =data)
			full_df = df.copy()
			print(full_df.tail())

for i in list_data:
	schedule.every(1).minutes.do(job,i)


while True:

	try:
		time_now = datetime.now()
		schedule.run_pending()
		time.sleep(1)
	except Exception as e:
		print(e)