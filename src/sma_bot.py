""""
08/04/2023 SMA Bot
Strategy: Determine the trend with sma20_1d / based off trend
buy/sell to open around the sma20_15m - 0.1% under and 0.3% above
"""

# import the necessary libraries

import ccxt
import pandas as pd
import numpy as np
from datetime import date, datetime, timezone, tzinfo
import time, schedule
import matplotlib.pyplot as plt

import dotenv
import ast
import os

# Load variables from the .env file
dotenv.load_dotenv(dotenv.find_dotenv(".env"))
os.environ["API_KEY"] = os.getenv("API_KEY")
os.environ["API_SECRET"] = os.getenv("API_SECRET")
os.environ["symbol"] = os.getenv("symbol")
os.environ["pos_size"] = os.getenv("pos_size")
os.environ["params"] = os.getenv("params")
os.environ["target"] = os.getenv("target")

# connect to the exchange
phemex = ccxt.phemex({
    'enableRateLimit': True,
    'apiKey': os.environ["API_KEY"],
    'secret': os.environ["API_SECRET"]
})

# Set Parameters
symbol = os.environ["symbol"] #symbol to trade
pos_size = int(os.environ["pos_size"]) # position size
params = ast.literal_eval(os.environ["params"])
target = int(os.environ["target"])

# Ask Bid
def ask_bid():
    """" ask_bid()[0] == ask"""
    ob = phemex.fetch_order_book(symbol=symbol) # returns the orderbook object wich is a dictionary
    bid = ob['bids'][0][0]
    ask = ob['asks'][0][0]
    return ask, bid

# Open Positions
def open_positions():

    pos_dict = phemex.fetch_positions(params=params)
    for i in range(len(pos_dict)):
        try:
            if pos_dict[i]['info']['symbol'] == symbol:
                position = pos_dict[i]
        except Exception as exc:
            print('Error fetching open positions')

    open_positions_side = position['info']['side']
    open_positions_size = position['info']['size']

    if open_positions_side == ('Buy'):
        openpos_bool = True
        long = True
    elif open_positions_side == ('Sell'):
        openpos_bool = True
        long = False
    else:
        openpos_bool = False
        long = None
        
    return position, openpos_bool, open_positions_size, long


# Determine the trend with the simple moving average 20 periods 1 day
#  FIND DAILY SMA 20
def sma20_1d():

    print('####################### Starting Daily SMA #######################')

    # FETCHING DATA FROM PHEMEX
    timeframe = '1d' # what is the fequency of the bars?
    num_bars = 1000 # how many bars of data will this fetch?
    bars = phemex.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=num_bars)

    # BUILDING A DATAFRAME FROM THIS DATA
    df_1d = pd.DataFrame(bars, columns=['timestamp','open','high','low','close','volume'])
    df_1d['timestamp'] = pd.to_datetime(df_1d['timestamp'], unit='ms') # change from milisecond timestamp

    # CALCULATE SMA20d
    df_1d['sma20_1d'] = df_1d['close'].rolling(20).mean()

    # if bid < sma20_1d then BEARISH, if bid > sma20_1d then BULLISH
    bid = ask_bid()[1]
    df_1d.loc[df_1d['sma20_1d']>bid, 'sig'] = 'SELL'
    df_1d.loc[df_1d['sma20_1d']<bid, 'sig'] = 'BUY'
 
    return df_1d

# Calculate the sma20_15m

#  FIND 15MINUTE SMA, FIGURE OUT IF BUY OR SELL BASED ON bid vs sma20_1d, if bid < sma20_1d then SELL
def sma20_15m():

    print('####################### Starting 15m SMA #######################')

    # FETCHING DATA FROM PHEMEX
    timeframe = '15m' # what is the fequency of the bars?
    num_bars = 1000 # how many bars of data will this fetch?
    bars = phemex.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=num_bars)

    # BUILDING A DATAFRAME FROM THIS DATA
    df_15m = pd.DataFrame(bars, columns=['timestamp','open','high','low','close','volume'])
    df_15m['timestamp'] = pd.to_datetime(df_15m['timestamp'], unit='ms') # change from milisecond timestamp

    # CALCULATE SMA20_15m
    df_15m['sma20_15m'] = df_15m['close'].rolling(20).mean()

    # BUY PRICE 1+2 and SELL PRICE 1+2
    df_15m['bp_1'] = df_15m['sma20_15m'] * 1.001 # sma20_15m 0.1% under and 0.3%over 
    df_15m['bp_2'] = df_15m['sma20_15m'] * 0.997
    df_15m['sp_1'] = df_15m['sma20_15m'] * 0.999
    df_15m['sp_2'] = df_15m['sma20_15m'] * 1.003
    
    return df_15m

# Kill Switch
# CREATE A KILL_SWITCH
def kill_switch():

    print('starting kill switch')
    openposi = open_positions()[1]
    kill_size = open_positions()[2]
    long = open_positions()[3]

    while openposi == True:
        print('starting kill switch loop till limit fill..')

        phemex.cancel_all_orders(symbol=symbol)
        openposi = open_positions()[1]
        kill_size = open_positions()[2]
        long = open_positions()[3]

        ask = ask_bid()[0]
        bid = ask_bid()[1]

        if long == False:
            phemex.create_limit_buy_order(symbol=symbol, amount=kill_size, price=bid, params=params)
            print(f"just made a BUY order to close order of {kill_size}|{symbol} at ${bid}")
            print('sleeping for 30 seconds to see if it fills')
            time.sleep(30)
        elif long == True:
            phemex.create_limit_sell_order(symbol=symbol, amount=kill_size, price=ask, params=params)
            print(f"just made a BUY order to close order of {kill_size}|{symbol} at ${ask}")
            print('sleeping for 30 seconds to see if it fills')
            time.sleep(30)
        else:
            print("++++++ Something I didn't expect in kill switch function")

        openposi = open_positions()[1]
    return

# OPEN POSITIONS FOR symbol
def open_position_for_symbol(symbol):
    pos_dict = phemex.fetch_positions(params=params)
    for i in range(len(pos_dict)):
        try:
            if pos_dict[i]['info']['symbol'] == "ETHUSD":
                return pos_dict[i]
        except Exception as exc:
            print('Error fetching open positions')

# PNL Close
def pnl_close():

    current_price = ask_bid()[1]
    # if hit target, close
    print("checking to see if it is time to exit...")
    params = {"type":"swap", "code":"USD"}
    pos_dict = open_positions()[0]
    print(pos_dict)
    side = pos_dict["side"]
    #size = pos_dict["contracts"]
    entry_price = float(pos_dict["entryPrice"])
    leverage = float(pos_dict["leverage"])

    print(f'side:{side} | entry_price:{entry_price} | leverage:{leverage}')

    if side == 'long':
        diff = current_price - entry_price
    else:
        diff = entry_price - current_price
    
    try:
        percentage = round(((diff/entry_price)*leverage), 10)
        print(percentage)
    except:
        percentage = 0
        print(percentage)

    print(f'diff:{diff} | percentage:{percentage}')
    pnl = percentage*100
    #pnl = 26
    
    print(f"this is our pnl {pnl}")

    pnlclose = False
    in_position = False

    if pnl > 0:
        in_position = True
        print("we are in a winning position")
        if pnl > target:
            print(f':) :) :) starting the kill switch becaue we hit our target:{target}')
            pnlclose = True
            kill_switch()
    elif pnl <0:
        print("we are in a loosing position but holding on")
        in_position = True
    else:
        print("we are not in a position")

    return pnlclose, in_position # pnl_close()[0] == pnlclose, pnl_close()[1] == in_position, size 


# -----------------BOT---------------------------
def bot():
    print("--------------------BOT---------------------------------")
    df_1d = sma20_1d()
    df_15m = sma20_15m()
    ask, bid = ask_bid()
    in_position = pnl_close()[1]

    sig = df_1d.iloc[-1]['sig']
    #sig = 'SELL'
    open_size = pos_size/2

    if in_position == False:
        if sig == "BUY":
            print('making opening order as a BUY')
            bp_1 = df_15m.iloc[-1]['bp_1']
            bp_2 = df_15m.iloc[-1]['bp_2']
            print(f'Making BUY order at bp1:{bp_1} & bp2:{bp_2}')

            phemex.cancel_all_orders(symbol=symbol)
            phemex.create_limit_buy_order(symbol=symbol, amount=open_size, price=bp_1, params=params)
            phemex.create_limit_buy_order(symbol=symbol, amount=open_size, price=bp_2, params=params)

            time.sleep(30)
        else:
            print("making opening order as a SELL")
            sp_1 = df_15m.iloc[-1]['sp_1']
            sp_2 = df_15m.iloc[-1]['sp_2']
            print(f'Making SELL order at sp1:{sp_1} & sp2:{sp_2}')

            phemex.cancel_all_orders(symbol=symbol)
            phemex.create_limit_sell_order(symbol=symbol, amount=open_size, price=sp_1, params=params)
            phemex.create_limit_sell_order(symbol=symbol, amount=open_size, price=sp_2, params=params)

            time.sleep(30)
    else:
        print("we are in position already, so not making new orders...")

# bot()

schedule.every(28).seconds.do(bot)

while True:
    try:
        schedule.run_pending()
    except Exception as e:
        print('+++++ MAYBE INTERNET PROB OR SOMETHING HAPPENNED')
        print(e)