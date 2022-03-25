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
from config.config import *
from config.function import *
import time

import schedule


os.system('cls')
cs = Console()
cs.log("Client")
cs.log(host,port)
host = "localhost"
port = 8090
debug = True

url = f"http://{host}:{port}"
cs.log("Try to get Connection : "+url)
r = requests.get(url)
cs.log(r.text)
name = "XAUUSD"#input('Enter Symbol Name :')
timeframe = "M1"
num_bars= 200
signal = 0
count = 0
triger_signal_init = 0
lot = 0.02	
comment = f'Ichimoku_{timeframe}'

TOKEN = ""
CHAT_ID = ""		

names = ["GOLD"]

def message(symbol,ut,Type):
	time_now = datetime.now()
	MESSAGE = f"symbol : {symbol} ,\n\n Zone De Recherche {Type}\n\n time = {time_now}\nUT : {ut}\n\n\t Strat : Ichimoku_{ut}"
	r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE}')
	cs.log(r.status_code)


def worker(name,timeframe,num_bars):
	# M =name,timeframe)
	triger_signal = 0
	route_data = f"{url}/ichimoku/{name}/{timeframe}/{num_bars}"
	r2 = requests.get(route_data)
	data = json.loads(r2.text)
	df = pd.DataFrame(data)
	# M =data)
	full_df = df.copy()
	# M =full_df)
	last_df = df.tail(1)
	last_signal = last_df['Strategy'][-1]

	# M ="-"*20,signal,"-"*20)
	# M =f"Last_Message_{signal}\t:\n{last_df}")
	# M =f"Last Signal_{signal}\t: {last_signal}")datetime.now()

	if str(last_signal) == 'buy':
		triger_signal_name = "buy"
		triger_signal = 1
	if str(last_df) == 'sell':
		triger_signal_name = "sell"
		triger_signal = -1
	
	data = {"name":name,
			"timeframe":timeframe,
			"last Signal": last_signal,
			"Triger":triger_signal,
			}
	cs.log(data)
	return data
	# compart_triger = f"Triger_ini | triger_signal \t:\t{triger_signal_init}|{triger_signal} "
	# M =compart_triger)
	# if triger_signal_init == triger_signal:
	# 	cs.M ="Une Action est en Court",justify='center',style='magenta')
	# 	open_trade_buy(action = triger_signal_name, symbol=symbol, lot=lot, deviation=20, comment=comment)

	# if triger_signal_init != triger_signal:
	# 	M =f"Triger_ini != triger_signal \t:\t{triger_signal_init}|{triger_signal} ")
	# 	cs.M ="Action Possible",justify='center',style='cyan')
	# 	# open_trade_buy(action = triger_signal_name, symbol=symbol, lot=lot, deviation=20, comment=comment)
	# 	triger_signal_init = triger_signal


def position(name,Type,timeframe):
	route=f"/open_position/{name}/{timeframe}/{Type}/{comment}/{lot}"
	req = requests.get(url+route)

def job():
	os.system('cls')
	time_now = datetime.now()
	for name in names :
		cs.log("\n","-"*120)
		cs.log(name)
		M1 = worker(name,"M1",num_bars)
		M3 =worker(name,"M3",num_bars)
		M5 =worker(name,"M5",num_bars)
		M15 =worker(name,"M15",num_bars)
		# H1 =worker(name,"H1",num_bars)
		if M1["name"] == M3['name'] == M5["name"] == M15['name'] :
			cs.log("Name Ok")
			if M1["last Signal"] == None or M1["last Signal"] != 0:
				if M1["last Signal"] != None or M1["last Signal"] == 0  :
					print(M1["last Signal"])
					cs.log("Get Stoch")
					route = f"/stochc/{name}/M1/200"
					r = requests.get(url+route)
					# cs.log(r.text)
					data = json.loads(r.text)

					cs.log(data)
					triger = data['Triger']
					if triger == 0:
						pass
					else:
						# route_data = f"/sup_res/{name}/{timeframe}/{num_bars}"
						# r2 = requests.get(url+route_data)
						# data = json.loads(r2.text)
						# df = pd.read_json(data)
						# # cs.log(data)
						# full_df = df.copy()
						# # cs.log(full_df.tail(1))
						# price = full_df['close'][-1]

						# last_rsi = full_df['rsi'][-1]
						# prev_rsi = full_df['rsi yersteday'][-1]

						# last_sma_fast = full_df["SMA fast"][-1]
						# last_sma_slow = full_df["SMA slow"][-1]

						# last_res = full_df["smooth resistance"][-1]
						# last_supp = full_df["smooth support"][-1]

						# last_signal = full_df["signal"][-1]

						# time_data = full_df.index[-1]

						# data = {
						# 		"time" : time_data,
						# 		"name" : name,
						# 		"timeframe" : timeframe,
						# 		"Last resistance" : last_res,
						# 		"Last support" : last_supp,
						# 		"Last Price" : price,
						# 		"Last RSI 7P" : last_rsi,
						# 		"Prev RSI 7P" : prev_rsi,
						# 		"SMA fast 10P" : last_sma_fast,
						# 		"SMA slow 21P" : last_sma_slow,
						# 		"Last_Signal" : last_signal,
						# }

						# # cs.log()
						# cs.log(data)
						# (data['time'])
						if M1["last Signal"] == "sell":
							# message(name,ut="M1",Type=M1["last Signal"])
							position(name=name,Type="sell",timeframe="M1")

						if M1["last Signal"] == 'buy':
							# Type = 1
							# position(name=name,Type="buy",timeframe="M1")
							message(name,ut="M1",Type=M1["last Signal"])

						print(triger , M1["last Signal"])
						# verif = chek_take_position(symbol=name,comment=comment,Type=Type)
						# cs.log(verif)
						# if triger == 1:
						# 	cs.log("buy")
						# 	message(name,ut="M1",Type=M1["last Signal"])
						# 	position(name=name,Type="buy",timeframe="M1")
						# 	# sys.exit()
						# #
						# if triger == -1:
						# 	cs.log('Sell')
						# 	message(name,ut="M1",Type=M1["last Signal"])
						# 	position(name=name,Type="sell",timeframe="M1")
							# sys.exit()

			else:
				cs.log("TimeFrame not ok")
				cs.log(f"Time :{time_now} MA1:{M1['last Signal']} M3:{M3['last Signal']}, M5:{M5['last Signal']} , M15 : {M15['last Signal']}")

	time.sleep(60)




schedule.every(1).minutes.do(job)


while True:
	try:
		time_now = datetime.now()
		schedule.run_pending()
		time.sleep(1)
	except Exception as e:
		print(e)