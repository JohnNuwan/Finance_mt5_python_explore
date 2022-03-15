import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
 
pd.set_option('display.max_columns', 500) 
pd.set_option('display.width', 1500) 
 
if not mt5.initialize():
    print("initialize failed")
    mt5.shutdown()
 
# account="HIDDEN"
# authorized=mt5.login()
# if authorized:
#     print("Authorized")
# else:
#     print("failed to connect at account #{}, error code: {}".format(account, mt5.last_error()))
 
cndl_72 = mt5.copy_rates_from_pos("GER40.cash", mt5.TIMEFRAME_M1, 1, 144)
cndl_72_df = pd.DataFrame(cndl_72) 
cndl_72_df['time']=pd.to_datetime(cndl_72_df['time'], unit='s') 
cndl_72_df.rename(columns={'time': 'date', 'tick_volume' : 'volume'}, inplace=True)
cndl_72_df.set_index('date', inplace=True)
cndl_72_df.drop(['spread','real_volume'], axis=1, inplace=True)
 
macd = cndl_72_df.ta.macd(close='close', fast=12, slow=26, signal=9)
 
macd_plot = mpf.make_addplot(macd["MACD_12_26_9"], panel=1, color='fuchsia', title="MACD")
macd_hist_plot = mpf.make_addplot(macd["MACDh_12_26_9"], type='bar', panel=1) 
macd_signal_plot = mpf.make_addplot(macd["MACDs_12_26_9"], panel=1, color='b')
plots = [macd_plot, macd_signal_plot, macd_hist_plot]
 
mpf.plot(cndl_72_df, type='candle', style='yahoo', addplot=plots)