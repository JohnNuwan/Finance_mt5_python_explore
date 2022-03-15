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

name = "XAUUSD"#input('Enter Symbol Name : ')
timeframe = "M1"
num_bars= 200
signal = 0
count = 0
triger_signal_init = 0
lot = input("Taille Lots :  ")
comment = f'Ichimoku_{timeframe}'
cs = Console()

TOKEN = "1801058128:AAETqJbJMjVUt6ewpjYL2ZVIU8wzIlrzJL4"
CHAT_ID = "@Forex_free_perfect"

def message(symbol,ut,Type):
	time_now = datetime.now()
	MESSAGE = f"symbol : {symbol} ,\n\n Zone De Recherche {Type}\n\n time = {time_now}\nUT : {ut}\n\n\t Strat : Ichimoku_{ut}"
	r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE}')
	print(r.status_code)


def open_trade_buy(symbol, lot,  deviation, comment):
	'''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
	'''
	try:
		lot = lot
		symbol = name
		point = mt5.symbol_info(symbol).point
		price = mt5.symbol_info_tick(symbol).ask
		deviation = deviation
		comment = comment
		request = {
		    "action": mt5.TRADE_ACTION_DEAL,
		    "symbol": symbol,
		    "volume": lot,
		    "type": mt5.ORDER_TYPE_BUY,
		    "price": price,
		    "sl": price - 100 * point,
		    "tp": price + 100 * point,
		    "deviation": deviation,
		    "magic": 234000,
		    "comment": comment,
		    "type_time": mt5.ORDER_TIME_GTC,
		    "type_filling": mt5.ORDER_FILLING_IOC,
		}
		 
		# envoie une demande de trading
		result = mt5.order_send(request)
		# vérifie le résultat de l'exécution
		print("1. order_send(): buy {} {} lots à {} avec une déviation={} points".format(symbol,lot,price,deviation));
		if result.retcode != mt5.TRADE_RETCODE_DONE:
		    print("2. order_send a échoué, retcode={}".format(result.retcode))
		   # demande le résultat sous forme de dictionnaire et l'affiche élément par élément
		    result_dict=result._asdict()
		    for field in result_dict.keys():
		        print("   {}={}".format(field,result_dict[field]))
		 # s'il s'agit de la structure d'une requête de trading, elle est affichée également élément par élément
		        if field=="request":
		            traderequest_dict=result_dict[field]._asdict()
		            for tradereq_filed in traderequest_dict:
		                print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
		
		print('_'*12)
		print(type(triger_signal_name))
		
		# print(choix(action = action, symbol=name, lot=lot, deviation=20, comment=comment))

		if rsi <= 30 or rsi >= 70:
			choix(action = action, symbol=name, lot=lot, deviation=20, comment=comment)
			# message(name,timeframe,triger_signal_name)
	except Exception as e:
		print(e)

def open_trade_sell(symbol, lot,  deviation, comment):
	'''https://www.mql5.com/en/docs/integration/python_metatrader5/mt5ordersend_py
	'''
	try:
		lot = lot
		# symbol = name
		print(symbol)
		point = mt5.symbol_info(symbol).point
		price = mt5.symbol_info_tick(symbol).ask
		deviation = 20
		request = {
		    "action": mt5.TRADE_ACTION_DEAL,
		    "symbol": symbol,
		    "volume": lot,
		    "type": mt5.ORDER_TYPE_BUY,
		    "price": price,
		    "sl": price - 100 * point,
		    "tp": price + 100 * point,
		    "deviation": deviation,
		    "magic": 234000,
		    "comment": "python script open",
		    "type_time": mt5.ORDER_TIME_GTC,
		    "type_filling": mt5. ORDER_FILLING_IOC,
		}
		 
		# envoie une demande de trading
		result = mt5.order_send(request)
		# vérifie le résultat de l'exécution
		print("1. order_send(): buy {} {} lots à {} avec une déviation={} points".format(symbol,lot,price,deviation));
		if result.retcode != mt5.TRADE_RETCODE_DONE:
		    print("2. order_send a échoué, retcode={}".format(result.retcode))
		   # demande le résultat sous forme de dictionnaire et l'affiche élément par élément
		    result_dict=result._asdict()
		    for field in result_dict.keys():
		        print("   {}={}".format(field,result_dict[field]))
		 # s'il s'agit de la structure d'une requête de trading, elle est affichée également élément par élément
		        if field=="request":
		            traderequest_dict=result_dict[field]._asdict()
		            for tradereq_filed in traderequest_dict:
		                print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))      
		return result, buy_request
	except Exception as e:
		print(e)


def choix(action,symbol,deviation,lot,comment):
	print('\n','-'*30)
	print("Action Dans La Variable Choix : ",action)
	print(type(action))
	action = str(action)
	print(action,type(action))
	open_trade_buy(action, symbol, lot,  deviation, comment)
	if action == str('buy'):
		prin("Action est un Buy On Ouvre une Position ")
		sys.exit()

	if action == str('sell'):
		prin("Action est un Sell On Ouvre une Position ")
		open_trade_sell(action, symbol, lot,  deviation, comment)
		sys.exit()
	if action != 'sell' or action != "buy":
		print(action,type(action)) 
	else : 
		print(f"Error Choix {action} != buy or sell")

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

	
	
	action = f"{last_signal}"
	print('Action :',action,triger_signal)
	print(type(str(action)))
	
	if action != None:
		print()
		print(action)
		print()
		if str(action) == 'buy':
			print('buy')
			triger_signal = 1

		if str(action) == 'sell':
			print('Sell')
			triger_signal = -1
		
		compart_triger = f'signal {triger_signal_init} || Last Signal : {last_signal} '
		print(compart_triger)

		
		if triger_signal_init == triger_signal:
			# if triger_signal != None:
				cs.print("Une Action est en Court",justify='center',style='magenta')

				if triger_signal == 1:
					open_trade_buy(symbol="XAUUSD", lot=lot,  deviation=20, comment=comment)

				if triger_signal == -1:
					open_trade_buy(symbol="XAUUSD", lot=lot,  deviation=20, comment=comment)
				

		if triger_signal_init != triger_signal:
			# if triger_signal != None:
				print(f"Triger_ini != triger_signal \t:\t{triger_signal_init}|{triger_signal} ")
				cs.print("Action Possible",justify='center',style='cyan')
				message(name,timeframe,last_signal)
				# choix(action = action, symbol=name, lot=lot, deviation=20, comment=comment)
				# open_trade_sell(symbol="XAUUSD", lot=lot,  deviation=20, comment=comment)
				if triger_signal == 1:
					open_trade_buy(symbol="XAUUSD", lot=lot,  deviation=20, comment=comment)

				if triger_signal == -1:
					open_trade_buy(symbol="XAUUSD", lot=lot,  deviation=20, comment=comment)

				triger_signal_init = triger_signal
		
	print(f"Triger\t:\t{triger_signal}")
	signal += 1

	time.sleep(5)