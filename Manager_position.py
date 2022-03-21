
import os 
import sys
os.system('cls')

import time 
import pandas as pd
import MetaTrader5 as mt5
from rich import print
from termcolor import colored, cprint


DISCORD_URL:"https://discordapp.com/api/webhooks/920233912721113128/7o77SZI2EDkJbUmF-zO2VbpQm98leaTxa_b1J7uQ4dFHkO9299he9aQz_ivvX3AbMKm9"


# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
	print("initialize() failed, error code =",mt5.last_error())
	quit()
 
# check the presence of open positions
positions_total=mt5.positions_total()
if positions_total>0:
	print("Total positions=",positions_total)
else:
	print("Positions not found")

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
# def changeslpl(ticket,pair,pos_type,SL,comment):
# 	request = {
# 		"action": mt5.TRADE_ACTION_SLTP,
# 		"symbol": pair,
# 		"type": pos_type,
# 		"position": ticket,
# 		"sl": SL,
# 		"deviation": 20,
# 		"magic": ea_magic_number,
# 		"comment": comment
# 		"type_time": mt5.ORDER_TIME_GTC,
# 		"type_filling": mt5.ORDER_FILLING_FOK,
# 	}
# 	#// perform the check and display the result 'as is'
# 	result = mt5.order_send(request)

# 	if result.retcode != mt5.TRADE_RETCODE_DONE:
# 		print("4. order_send failed, retcode={}".format(result.retcode))

# 		print(" result",result)
def RE_split():
	# get the list of positions on symbols whose names contain "*USD*"
	usd_positions=mt5.positions_get()
	if usd_positions==None:
		print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
	elif len(usd_positions)>0:
		print("positions_get(group=\"*USD*\")={}".format(len(usd_positions)))
		# display these positions as a table using pandas.DataFrame
		df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
		df['time'] = pd.to_datetime(df['time'], unit='s')
		df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
		df = df.set_index("time")
		print(df)

		for row in df.itertuples():
			print(row)
			if row.comment =="Pct M1"or"ichimoku" or "Renfort M1" or "python Meanreverse" or"python M1"or"python M3" or"python M5"or"python M15" or 'Alligator M1':
				if calc_dif(row) >= 0.143:
					if row.volume > 0.02:
						print("-"*60)
						print("symbole\t:\t",row.symbol)
						print("profit\t:\t",row.profit)
						print("open price\t:\t",row.price_open)
						print("Current price\t:\t",row.price_current)

						print("Changement\t:\t",calc_dif(row))
						print("split")
						try:
							print("close")
							symbol = row.symbol
							action = row.type
							position_id=row.ticket
							lot = row.volume
							if action == 1:
								trade_type = mt5.ORDER_TYPE_BUY
								price = mt5.symbol_info_tick(row.symbol).ask
							elif action == 0 :
								trade_type = mt5.ORDER_TYPE_SELL
								price = mt5.symbol_info_tick(row.symbol).bid

							request={
								"action": mt5.TRADE_ACTION_DEAL,
								"symbol": symbol,
								"volume": lot/2,
								"type": trade_type,
								"position": position_id,
								"price": price,
								"deviation": 20,
								"magic": 234000,
								"comment": "HOLD",
								"type_time": mt5.ORDER_TIME_GTC,
								"type_filling": mt5.ORDER_FILLING_IOC,
							}
							# send a trading request
							result=mt5.order_send(request)
							print(result)
							requests.post(DISCORD_URL, json=request)
							if result.retcode != mt5.TRADE_RETCODE_DONE: 
								print(colored(f"Order closing failed: {result.retcode}"),'red')#.format())

							else:
								print(colored("closed correctly","blue"))
							
						except Exception as e:
							print(e)
							
					try:
						chang = calc_dif(row)
						print(chang)
						if row.type == 0:
							SL = row.price_open + (chang/2)
						
						if row.type == 1:
							SL = row.price_open - (chang/2)
						
						print(colored("-"*60,"blue"))
						print(f"{row.symbol} Price Open : {row.price_open} ")
						print(f"{row.symbol} New SL : {SL} ")
						print(f"{row.symbol} %Chang : {chang} % ")
						request = {
							"action": mt5.TRADE_ACTION_SLTP,
							"symbol": row.symbol,
							"type": row.type,
							"position": row.ticket,
							"sl": SL,
							"deviation": 20,
							"magic": 666,
							"comment": "python Split",
							"type_time": mt5.ORDER_TIME_GTC,
							"type_filling": mt5.ORDER_FILLING_FOK,
							"ENUM_ORDER_STATE": mt5.ORDER_FILLING_IOC,
							}

						## perform the check and display the result 'as is'
						result = mt5.order_send(request)
						if result.retcode != mt5.TRADE_RETCODE_DONE:
							print("-"*60) 
							print(f"{row.symbol}\t:\n\t\tOrder Change failed: {result.retcode} \n\t\t Profit : \t{row.profit}$")
						# # sys.exit()

						else:
							print("Change correctly")
					except Exception as e:
						print(e)

		for row in df.itertuples():
			print(row)
			if row.comment =="Ichimoku_M1" or 'Reverse M1' or 'Renfort M1' or "python Meanreverse" or"python M1"or"python M3" or"python M5"or"python M15" or"python M250" or"python H1":
				if calc_dif(row) <= -0.65:
					if row.volume >= 0.02:
						print("-"*60)
						print("symbole\t:\t",row.symbol)
						print("profit\t:\t",row.profit)
						print("open price\t:\t",row.price_open)
						print("Current price\t:\t",row.price_current)

						print("Changement\t:\t",calc_dif(row))
						print("split")
						try:
							print("close")
							symbol = row.symbol
							action = row.type
							position_id=row.ticket
							lot = row.volume
							if action == 1:
								trade_type = mt5.ORDER_TYPE_BUY
								price = mt5.symbol_info_tick(row.symbol).ask
							elif action == 0 :
								trade_type = mt5.ORDER_TYPE_SELL
								price = mt5.symbol_info_tick(row.symbol).bid

							request={
								"action": mt5.TRADE_ACTION_DEAL,
								"symbol": symbol,
								"volume": lot,
								"type": trade_type,
								"position": position_id,
								"price": price,
								"deviation": 20,
								"magic": 234000,
								"comment": "HOLD",
								"type_time": mt5.ORDER_TIME_GTC,
								"type_filling": mt5.ORDER_FILLING_IOC,
							}
							# send a trading request
							result=mt5.order_send(request)
							print(result)
							requests.post(DISCORD_URL, json=request)
							if result.retcode != mt5.TRADE_RETCODE_DONE: 
								print(colored(f"Order closing failed: {result.retcode}"),'red')#.format())

							else:
								print(colored("closed correctly","blue"))
							
						except Exception as e:
							print(e)
		
		for row in df.itertuples():					
			if row.comment =="HOLD":
				if calc_dif(row) >= 0.2:
					if row.volume >= 0.02:
						print("-"*60)
						print("symbole\t:\t",row.symbol)
						print("profit\t:\t",row.profit)
						print("open price\t:\t",row.price_open)
						print("Current price\t:\t",row.price_current)

						print("Changement\t:\t",calc_dif(row))
						print("split")
						# changeslpl(ticket,pair,pos_type,SL,tp,comment)



while 1:
	try:
		RE_split()
		time.sleep(5)
	except Exception as e:
		raise e