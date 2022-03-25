import pandas as pd 
import requests
import os


from rich import print
import json

from datetime import datetime
from rich.console import Console

os.system('cls')

symbol = "GOLD"#"UK100.cash"#"GER40.cash"
comment = "HOLD"
Type = 0

host = "localhost"
port = 8090

cs = Console()
url = f"http://localhost:8090"
print(url)

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
						# 		"Time" : row.time,#pd.to_datetime(row.time, unit='s'),

						# 		"Name" : row.symbol,
						# 		"Id_ticker" : row.identifier,
						# 		"Profit" :row.profit,
						# 		"Lot" : row.volume,
						# 		"Comment" : row.comment,
						# 		'Type' : row.type
						# 		}
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
					# 		"time" : row.time,
					# 		"Name": symbol,
					# 		"Nb Pos" : count,
					# 		"Lot" : volume_count,
					# 		"Type" : Type
					# 	}
					# # df = pd.DataFrame(data_check)
					# print(data_check)
					# return data_check#df.to_json()
			
			# else :
				# return "Note Data"
	except Exception as e:
		return e


verif = chek_take_position(symbol=symbol,comment=comment,Type=Type)
print("\n",verif)

print(verif['Total'])

	