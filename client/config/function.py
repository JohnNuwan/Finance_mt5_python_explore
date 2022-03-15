import pandas as pd 
import requests
import os

from config.config import *
from rich import print
import json

from datetime import datetime

os.system('cls')

# symbol = "BTCUSD"#"UK100.cash"#"GER40.cash"
# comment = "HOLD"#"Ichimoku_M1"


url = f"http://{host}:{port}"
print(url)

def chek_take_position(symbol,comment,Type):
	url = f"http://{host}:{port}"
	try:
		route_position = "/positions_en_court"
		url = f"{url}{route_position}"
		cs.log(url)
		count = 0
		volume_count = 0
		itme_now = datetime.now()
		recv_data = requests.get(url)
		encode_data = json.loads(recv_data.text)
		# cs.log(encode_data)
		df = pd.read_json(encode_data)
		list_frame = []

		df.drop(columns=['external_id','time_msc', 'reason','time_update','time_update_msc'],inplace=True)
		df['time'] = pd.to_datetime(df['time'], unit='s')
		df.set_index(df['time'],inplace=True)
		# print(df)
		# symbol_df_filtre = pd.DataFrame()
		for row in df.itertuples():
			# print(f"{row.symbol}      {row.type}      {row.comment}      {row.profit}      {row.volume}")
			if row.symbol == symbol:#
				# print(row.symbol,"ok")
				if row.comment == comment:
					if row.type == Type:
						volume_count += row.volume
						# print(row)
						# print(row.time,row.symbol,row.profit,row.volume,row.comment,row.identifier,"ok")
						data_symbol = {
								"Time" : row.index,#pd.to_datetime(row.time, unit='s'),

								"Name" : row.symbol,
								"Id_ticker" : row.identifier,
								"Profit" :row.profit,
								"Lot" : row.volume,
								"Comment" : row.comment,
								'Type' : row.type
								}
						print(data_symbol)
						last_time = row.index
						# list_frame.append(row.time)
						# # print(type(data_symbol))
						# series = pd.Series(data_symbol)
			  
						# # print(series)
						# list_frame.append(series)
						count+=1
		data_check = {
				"time" : last_time,
				"Name": symbol,
				"Nb Pos" : count,
				"Lot" : volume_count,
				"Type" : Type
			}
		cs.log(data_check)
		return data_check
		
	except Exception as e:
		return e


# verif = chek_take_position(symbol=symbol,comment=comment)
# print(verif)

	