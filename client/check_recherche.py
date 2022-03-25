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
comment = None

TOKEN = ""
CHAT_ID = ""		

names = ["GOLD"]

def message(symbol,ut,Type):
	time_now = datetime.now()
	MESSAGE = f"symbol : {symbol} ,\n\n Zone De Recherche {Type}\n\n time = {time_now}\nUT : {ut}\n\n\t Strat : Ichimoku_{ut}"
	r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE}')
	cs.log(r.status_code)


def worker(name,timeframe,num_bars):
	triger_signal = 0
	route_data = f"{url}/ichimoku/{name}/{timeframe}/{num_bars}"
	r2 = requests.get(route_data)
	data = json.loads(r2.text)
	df = pd.DataFrame(data)
	full_df = df.copy()
	last_df = df.tail(1)
	last_signal = last_df['Strategy'][-1]


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
					if M1["last Signal"] == "buy":
						verif = chek_take_position(symbol=name,comment=comment,Type=0)
						print(verif)

					if M1["last Signal"] == "sell":
						verif = chek_take_position(symbol=name,comment=comment,Type=1)
						print(verif)
					# cs.log(verif)


			else:
				cs.log("TimeFrame not ok")
				cs.log(f"Time :{time_now} MA1:{M1['last Signal']} M3:{M3['last Signal']}, M5:{M5['last Signal']} , M15 : {M15['last Signal']}")

	time.sleep(60)




# schedule.every().seconds.do(job)
schedule.every(1).seconds.do(job)


while True:
	try:
		time_now = datetime.now()
		schedule.run_pending()
		time.sleep(1)
	except Exception as e:
		print(e)