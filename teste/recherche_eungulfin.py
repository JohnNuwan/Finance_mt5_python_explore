import ta
import numpy as np
import warnings
from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5
warnings.filterwarnings("ignore")
mt5.initialize()
from Chapter_08_MT5 import *


def engulfing(symbol):
    
    # Import / Features engineering
    df = MT5.get_data(symbol, 70, timeframe=mt5.TIMEFRAME_D1)
    
    
    df["Candle way"] = -1
    df.loc[(df["open"] - df["close"]) < 0, "Candle way"] = 1
    df["amplitude"] = np.abs(df["close"] - df["open"])
    
    
    buy = (df["Candle way"].shift(5).iloc[-1] == -1) and\
        (df["Candle way"].shift(4).iloc[-1] == -1) and\
        (df["Candle way"].shift(3).iloc[-1] == -1) and\
        (df["Candle way"].shift(2).iloc[-1] == -1) and\
        (df["Candle way"].shift(1).iloc[-1] == -1) and\
        (df["Candle way"].iloc[-1] == 1) and\
        (df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
        (df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
        (df["amplitude"].shift(1).iloc[-1]*1.5 < df["amplitude"].iloc[-1])
    
    
    
    sell = (df["Candle way"].shift(5).iloc[-1] == 1) and\
       (df["Candle way"].shift(4).iloc[-1] == 1) and\
       (df["Candle way"].shift(3).iloc[-1] == 1) and\
       (df["Candle way"].shift(2).iloc[-1] == 1) and\
       (df["Candle way"].shift(1).iloc[-1] == 1) and\
       (df["Candle way"].iloc[-1] == -1) and\
       (df["close"].shift(1).iloc[-1] < df["open"].iloc[-1]*(1+0.5/100)) and\
       (df["close"].shift(1).iloc[-1] > df["open"].iloc[-1]*(1-0.5/100)) and\
       (df["amplitude"].shift(1).iloc[-1] * 1.5< df["amplitude"].iloc[-1])
    

    return buy, sell

mt5.initialize()
# True = Live Trading and False = Screener
live = True

if live:
    current_account_info = mt5.account_info()
    print("------------------------------------------------------------------")
    print("Date: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Balance: {current_account_info.balance} USD, \t"
          f"Equity: {current_account_info.equity} USD, \t"
          f"Profit: {current_account_info.profit} USD")
    print("------------------------------------------------------------------")


info_order = {
    "GOLD": ["GOLD", 0.02],
    "EURUSD": ["EURUSD", 0.02],
    "DAX": ["[DAX40]", 0.2],
    "DJI": ["[DJI30]", 0.2],
    
}


start = datetime.now().strftime("%H:%M:%S") #"23:59:59"
while True:
    # Verfication for launch
    if datetime.now().weekday() not in (5,6): # If you want to trade only from Monday to Friday
        is_time = datetime.now().strftime("%H:%M:%S") == start 
    else:
        is_time = False

    
    # Launch the algorithm
    if is_time:

        # Open the trades
        for asset in info_order.keys():

            # Initialize the inputs
            symbol = info_order[asset][0]
            lot = info_order[asset][1]

            # Create the signals
            buy, sell = engulfing(symbol)

             # Run the algorithm
            if live:
                MT5.run(symbol, buy, sell,lot)

            else:
                print(f"Symbol: {symbol}\t"
                     f"Buy: {buy}\t"
                     f"Sell: {sell}")