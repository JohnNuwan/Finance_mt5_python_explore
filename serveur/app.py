
import os
import sys 


from fastapi import FastAPI, Request
import uvicorn

import MetaTrader5 as mt5

from rich import print
from rich.console import Console


import pandas as pd 
import numpy as np


from datetime import datetime 

import seaborn as sns
import matplotlib.pyplot as plt

import pytz

import ta 

from art import *

from config.config import *
from config.functions import *



os.system('cls')
logo = tprint(prog_name,font="wizard", chr_ignore=True)
cs = Console()

app = FastAPI()

sur_achat = 70
sur_vente = 30

path_ohlc = "./OHLC"
if not os.path.exists(path_ohlc):
	os.makedirs(path_ohlc)

@app.get('/')
async def home( request: Request):
	return {'status': 1, 'message': 'ok', 'Serveur': prog_name}
	# return {"Hello":"World" , "client_host": client_host}


@app.get('/positions_en_court')
async def teste():
	mt5.initialize()
	account_info=mt5.account_info()
	# get the list of positions on symbols whose names contain "*USD*"
	usd_positions=mt5.positions_get()
	if usd_positions==None:
		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
	elif len(usd_positions)>0:
		print("Total Positions {}".format(len(usd_positions)))
		# display these positions as a table using pandas.DataFrame
		df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
		print(df)
		return df.to_json()


@app.get('/position_total')
async def position_total():
	mt5.initialize()
	account_info=mt5.account_info()
	# get the list of positions on symbols whose names contain "*USD*"
	usd_positions=mt5.positions_get()
	if usd_positions==None:
		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
	elif len(usd_positions)>0:
		print("Total Positions {}".format(len(usd_positions)))
		return {"Total Positions" : len(usd_positions)}




# @app.get('/strategy_comment/{name}')
# async def strategy_comment(name:str):
# 	mt5.initialize()
# 	account_info=mt5.account_info()
# 	# get the list of positions on symbols whose names contain "*USD*"
# 	usd_positions=mt5.positions_get()
# 	if usd_positions==None:
# 		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
# 	elif len(usd_positions)>0:
# 		print("Total Positions {}".format(len(usd_positions)))
# 		# display these positions as a table using pandas.DataFrame
# 		df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
# 		print(df.columns)
# 		ensemble_1 = df.groupby('symbol')
# 		for i in ensemble_1:
# 			if i[0] == name:
# 				data = pd.DataFrame(i)
# 				for k in data.itertuples():
# 					print()
# 					data = k[1]
# 					print(type(data))
# 					print(data)
					
# 	return "Teste"


@app.get('/OHLC/{name}/{timeframe}/{num_bars}')
async def ohlc(name:str,timeframe:str,num_bars:int):
	df =  get_data(name, timeframe, num_bars)
	return df.to_json()


@app.get('/sup_res/{name}/{timeframe}/{num_bars}')
async def sup_res(name:str,timeframe:str,num_bars:int):
	df =  get_data(name, timeframe, num_bars)
	data = support_resistance(df, duration=6,spread=df['spread'][-1]).tail()
	return data.to_json()


@app.get('/stochc/{name}/{timeframe}/{num_bars}')
async def stoch(name:str,timeframe:str,num_bars:int):
	df =  get_data(name, timeframe, num_bars)
	print(df)
	#Create the "L14" column in the DataFrame
	df['L14'] = df['low'].rolling(window=14).min()
	#Create the "H14" column in the DataFrame
	df['H14'] = df['high'].rolling(window=14).max()
	#Create the "%K" column in the DataFrame
	df['%K'] = 100*((df['close'] - df['L14']) / (df['H14'] - df['L14']) )
	#Create the "%D" column in the DataFrame
	df['%D'] = df['%K'].rolling(window=3).mean()

	buy_entry = 0
	sell_entry = 0
	ovre_buy = 80
	over_sell = 20
	triger = 0

	if (df['%K'][-1] < df['%D'][-1])  & (df['%D'][-1] >= ovre_buy):
		triger = -1
		print("Sell")
	
	if (df['%K'][-1] > df['%D'][-1]) & (df['%D'][-1] <= over_sell):
		triger = 1
		print("buy")
	
	data = {
		"time" : df.index[-1],
		"name": name,
		"TimeFrame":timeframe,
		"Triger": triger,
		"Last %K": df['%K'][-1],
		"Last %D": df['%D'][-1]
	}
	
	print("\n\t","-"*30)
	print(data)
	return data#df.to_json()

@app.get('/ichimoku/{name}/{timeframe}/{num_bars}')
async def teste(name:str,timeframe:str,num_bars:int):
	df =  get_data(name, timeframe, num_bars)
	
	# Creation Mask 
	mask_chikou = df.copy()
	mask_tenkan = df.copy()
	mask_kijun = df.copy()
	mask_senkou = df.copy()
	mask_rsi = df.copy()
	

	mask_chikou['chikou'] = mask_chikou.close.shift(-26).dropna()
	mask_chikou.dropna(inplace=True)


	nine_periodf_high = mask_tenkan['high'].rolling(window= 9).max()
	nine_periodf_low = mask_tenkan['low'].rolling(window= 9).min()
	mask_tenkan['tenkan_sen'] = (nine_periodf_high + nine_periodf_low) /2

	# Kijun-sen (Base Line): (26-periodf high + 26-periodf low)/2))
	periodf26_high = mask_kijun['high'].rolling(window=26).max()
	periodf26_low = mask_kijun['low'].rolling(window=26).min()
	mask_kijun['kijun_sen'] = (periodf26_high + periodf26_low) / 2

	# Senkou Span A (Leadfing Span A): (Conversion Line + Base Line)/2))
	mask_senkou['senkou_span_a'] = ((mask_tenkan['tenkan_sen'] + mask_kijun['kijun_sen']) / 2).shift(26)
	# Senkou Span B (Leadfing Span B): (52-periodf high + 52-periodf low)/2))
	periodf52_high = mask_senkou['high'].rolling(window=52).max()
	periodf52_low = mask_senkou['low'].rolling(window=52).min()
	mask_senkou['senkou_span_b'] = ((periodf52_high + periodf52_low) / 2).shift(52)

	mask_rsi["RSI_4"] = ta.momentum.rsi(close=mask_rsi["close"], window=4, fillna=True)

	# Prise de chaque dernier valeur 
	last_close = df['close'][-1]
	last_chikou = mask_chikou['chikou'][-1]
	close_chikou = mask_chikou['close'][-1]
	last_tenkan = mask_tenkan['tenkan_sen'][-1]
	last_kijun = mask_kijun['kijun_sen'][-1]
	last_senkou_a = mask_senkou['senkou_span_a'][-1]
	last_senkou_b = mask_senkou['senkou_span_b'][-1]
	last_RSI_4 = mask_rsi['RSI_4'][-1]

	Condition_1 = 0
	Condition_2 = 0
	Condition_3 = 0
	Condition_4 = 0
	Condition_5 = 0
	Condition_6 = 0
	Condition_7 = 0

	type_trade = None
	if last_chikou < close_chikou:
		Condition_3 = -1
	
	if last_chikou > close_chikou:
		Condition_3 = 1
	
	if last_tenkan > last_kijun:
		Condition_2 = 1

	if last_tenkan < last_kijun:
		Condition_2 = -1
	
	if last_close > last_senkou_b :
		Condition_1 = 1

	if last_close < last_senkou_b :
		Condition_1 = -1

	if last_tenkan < last_senkou_b :
		message = f"tenkan_sen < senkou_span_b Condition 1 vente"
		# cs.print(f"Last senkou_span_b :{last_senkou_b}",justify='left')
		# cs.print(f"Last tenkan_sen :{last_tenkan}",justify='left')
		# buy_sell_sep(message,Type="Sell")
		Condition_4 = -1
	
	if last_tenkan > last_senkou_b :
		Condition_4 = 1

	if last_tenkan < last_senkou_a :
		Condition_5 = -1
	
	if last_tenkan > last_senkou_b :
		Condition_5 = 1

	if last_chikou < last_senkou_b :
		Condition_6 = -1
	
	if last_tenkan > last_senkou_b :
		Condition_6 = 1

	if last_RSI_4 > sur_achat :
		Condition_7 = -1
	
	if last_RSI_4 < sur_vente :
		Condition_7 = 1
			
	if Condition_1 == Condition_2 == Condition_3 == Condition_4  == Condition_5 == Condition_6  == 1:
		type_trade = 'buy'
	
	if Condition_1 == Condition_2 == Condition_3 == Condition_4 == Condition_5 == Condition_6 == -1:
		# buy_sell_sep("Sell NOW", Type="Sell")
		type_trade = "sell"
		
	
	parame = { name :{
					"time" : df.index[-1],
					"TimeFrame" : timeframe,
					'Last Close': last_close,
					'last_chikou': last_chikou,
					'close_chikou': close_chikou,
					'Tenkan' : last_tenkan,
					"kijun" : last_kijun,
					'Senkou__A' : last_senkou_a,
					"Senkou_B" : last_senkou_b,
					"RSI 7P" : last_RSI_4
					},
				"Strategy":{
						"name" : f'Ichimoku_{timeframe}',
						"last_close >|< last_senkou_b" : Condition_1,
						"last_tenkan >|< last_kijun" : Condition_2,
						"last_tenkan >|< last_senkou_a" : Condition_5,
						"last_tenkan >|< last_senkou_b" : Condition_4,
						"last_chikou >|< close_chikou" : Condition_3,
						"last_chikou >|< last_senkou_b" : Condition_6,
						f"last_RSI_4 >|< Sur Achat:{sur_achat} | Sur Vente: {sur_vente}" : Condition_7,

						"Trade Zone" : type_trade,
					}
			}
	print(parame)
	return parame
	

@app.get('/open_position/{name}/{timeframe}/{Type}/{comment}/{lot}')
async def open_position(name:str,timeframe:str,Type:str,comment:str,lot:float):
	try:
		data = {
				"Name" : name,
				"TimeFrame": timeframe,
				"Type" : Type,
				'Comment': comment,
				"Lot" : lot,
			}
		signal = open_trade_buy(action=Type, symbol=name, lot=lot,  deviation=20, comment=comment)
		print(signal)
		if signal == True:
			print(signal)
			print(data)
		else:
			return e
	except Exception as e:
		print(e)

	return data




if __name__ == '__main__':

	uvicorn.run(app, host=host, port=port, debug=debug)