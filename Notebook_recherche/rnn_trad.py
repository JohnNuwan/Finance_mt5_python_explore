

from MT5 import *
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import time
import pickle
import ta
from joblib import dump, load
import os
from sklearn.preprocessing import StandardScaler
import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout


path = "" # Ex: C:/Desktop/Python_for_finance_and_algorithmic_trading/ChapterN/Models



def feature_engineering(df):
    """ DON'T PUT THE SHIFT HERE"""
    
    # We copy the dataframe to avoid interferences in the data
    df_copy = df.copy()
    df_copy[["returns"]] = df_copy[["close"]].pct_change(1)

    # Create the SMAs
    df_copy["SMA 15"] = df_copy[["close"]].rolling(15).mean()
    df_copy["SMA 60"] = df_copy[["close"]].rolling(60).mean()
    
    # Create the volatilities
    df_copy["MSD 10"] = df_copy[["returns"]].rolling(10).std()
    df_copy["MSD 30"] = df_copy[["returns"]].rolling(30).std()
    
    # Create the Rsi
    RSI = ta.momentum.RSIIndicator(df_copy["close"], window= 14, fillna = False)
    df_copy["rsi"] = RSI.rsi()
    
    # STANDARDIZATION

    sc = StandardScaler()
    df_copy = df_copy[["SMA 15", "SMA 60", "MSD 10", "MSD 30", "rsi"]].dropna()
    df_copy_sc = sc.fit_transform(df_copy)

    return df_copy_sc

def X_3d_RNN(X_s, y_s, lag):

    # Simple verification
    if len(X_s) != len(y_s):
        print("Warnings")

    # Create the X_train
    X_train = []
    for variable in range(0, X_s.shape[1]):
        X = []
        for i in range(lag, X_s.shape[0]):
            X.append(X_s[i-lag:i, variable])
        X_train.append(X)
    X_train, np.array(X_train)
    X_train = np.swapaxes(np.swapaxes(X_train, 0, 1), 1, 2)

    # Create the y_train
    y_train = []
    for i in range(lag, y_s.shape[0]):
        y_train.append(y_s[i, :].reshape(-1,1).transpose())
    y_train = np.concatenate(y_train, axis=0)
    return X_train, y_train

   
def RNN_weights():
    # INITIALIZATION OF THE MODEL
    classifier = Sequential()

    # ADD LSTM LAYER
    classifier.add(LSTM(units = 10, return_sequences = True,
                      input_shape = (15,5,)))


    # LOOP WHICH ADD LSTM LAYER
    for _ in range(1):
        classifier.add(LSTM(units = 10, return_sequences = True))
        classifier.add(Dropout(0.50))

    # LAST LSTM LAYER BUT WITH return_sequences = False 
    classifier.add(LSTM(units = 10, return_sequences = False))


    # OUTPUT DENSE LAYER
    classifier.add(Dense(1, activation="sigmoid"))

    # COMPILE THE MODEL
    classifier.compile(loss="binary_crossentropy", optimizer="adam")

    return classifier

def RNN_cl_sig(symbol):
    """ Function for predict the value of tommorow using DNN model"""
    
    # Create the weights if there is not in the folder
    rnn_1 = RNN_weights()
    rnn_2 = RNN_weights()
    rnn_3 = RNN_weights()

    # Import trained weights
    rnn_1.load_weights(f"RNN_weights/RNN n3")
    rnn_2.load_weights(f"RNN_weights/RNN n34")
    rnn_3.load_weights(f"RNN_weights/RNN n31")
    
    # Take the lastest percentage of change 
    df = MT5.get_data(symbol, 700)
    
    # Features engeeniring
    data = feature_engineering(df)
    X_data, _ = X_3d_RNN(data, np.zeros([700,1]),15)
    X = X_data[-1:,:,:]
    print(np.shape(X))
    # Bagging
    pr1 = np.where(rnn_1.predict(X)==0, -1,1)
    pr2 = np.where(rnn_2.predict(X)==0, -1,1)
    pr3 = np.where(rnn_3.predict(X)==0, -1,1)
    
    # Find the signal
    buy = (pr1 + pr2 + pr3)[0][0] >=1
    sell = not buy
    
    
    return buy, sell



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
    "Bitcoin": ["BTCUSD", 1.00]
}


start = datetime.now().strftime("%H:%M:%S")
while True:
    # Verfication for launch
    if datetime.now().weekday() not in (5,6):
        is_time = datetime.now().strftime("%H:%M:%S") == start #"23:59:59"
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
            buy, sell = RNN_cl_sig(symbol)

             # Run the algorithm
            if live:
                MT5.run(symbol, buy, sell,lot)

            else:
                print(f"Symbol: {symbol}\t"
                     f"Buy: {buy}\t"
                     f"Sell: {sell}")
    time.sleep(1)

