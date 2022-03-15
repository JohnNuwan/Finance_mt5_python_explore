
import os
import requests
import time
import json
from config.config import *
from rich import print

import pandas as pd
os.system('cls')

symbol = "XAUUSD"
timeframe = "M1"
num_bars = 200
ovre_buy = 80
over_sell = 20


route = f"stochc/{symbol}/{timeframe}/{num_bars}"
url = f"http://{host}:{port}/{route}"


print(url)
count = 0
while count < 1000:
	r = requests.get(url)
	data = json.loads(r.text)
	df_stoch = pd.read_json(data)
	triger = 0
	if (df_stoch['%K'][-1] < df_stoch['%D'][-1])  & (df_stoch['%D'][-1] >= ovre_buy):
		print(df_stoch.tail(1))
		triger = -1
		print("Sell")
	
	if (df_stoch['%K'][-1] > df_stoch['%D'][-1]) & (df_stoch['%D'][-1] <= over_sell):
		triger = 1
		print(df_stoch.tail(1))
		print("buy")
	count +=1
	time.sleep(1)