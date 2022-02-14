import telegram
import pyupbit
import pandas as pd
import pandas_datareader.data as web
import datetime
import numpy as np
%matplotlib inline
import matplotlib.pyplot as plt
import math
import pyfolio as pf
import quantstats
plt.rcParams["figure.figsize"] = (10, 6) # (w, h)
import sys
from scipy.stats import rankdata
from scipy.stats import stats
from scipy.optimize import minimize
from datetime import datetime, timedelta
import pandas_datareader as pdr
from openpyxl import workbook 
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from sklearn.preprocessing import StandardScaler  # 표준화 패키지 라이브러리 
from sklearn.decomposition import PCA
from pypfopt import risk_models
from pypfopt.efficient_frontier import EfficientFrontier
import pypfopt as pypfopt

import pyupbit
import time
import calendar
import json



access = "VttO9jzrj6npxmQGdmMgNy0YkjCat77AOkJcpPXx"
secret = "7t5K14n3MvYkxM0ijOxcWWRcD91ESnkXFNIiWTvz"
upbit = pyupbit.Upbit(access, secret)
bot = telegram.Bot(token='5230064984:AAGTqmIcdO-H0vJbUu3aUzlQ4J8N9JE_sV0')
chat_id = 1673805200

def telegramlog(message):
       
    # 함수로 받은 문자열을 파이썬에서 출력 + 텔레그램 메시지로 전송
    print(datetime.now().strftime('[%y/%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%y/%m/%d %H:%M:%S] ') + message
    
    # Use your telegram chat_id
    bot.sendMessage(chat_id, text = strbuf)

def printlog(message, *args):
    # 함수로 받은 문자열을 파이썬에서 출력
    print(datetime.now().strftime('[%y/%m/%d %H:%M:%S]'), message, *args)

# 4시간봉, 최근 num_candle봉
def get_candle_high_low_range(crypto):
    df = pyupbit.get_ohlcv(crypto, interval = 'minute240', to=datetime.now()).tail(20)
    candle_high = max(df['high'])
    candle_low = min(df['low'])
    candle_high80 = candle_low + 0.8 * (candle_high - candle_low)
    candle_low20 = candle_low + 0.2 * (candle_high - candle_low)
    
    return candle_high, candle_low, candle_high80, candle_low20

def buy_crypto(crypto):
    current_price = pyupbit.get_current_price(crypto)
    unit = upbit.get_balance(ticker=crypto)
    # 매수 신호: 4시간봉 20개 동안 고가-저가 범위의 상단 80%보다 현재가가 높음. 이미 보유 중이면 추가 매수 안 함
    # (보유 개수 0일 때만 매수)
    if current_price > get_candle_high_low_range(crypto)[2] and str(unit)=='0':
        # 본인 계좌 예수금
        krw = upbit.get_balance(ticker="KRW")
        # crypto currency의 매도 호가 중 가장 낮은 호가
        orderbook = pyupbit.get_orderbook(tickers=crypto)[0]['orderbook_units'][0]['ask_price']
        # BTC, ETH, BCH, EOS, XRP
        amount = krw / (6 - len(upbit.get_balances())) - 0.01 * krw
        unit = amount / orderbook
        # 시장가 매수: 매수는 돈 얼마 넣는지로 나옴
        upbit.buy_market_order(crypto, amount)
        telegramlog("BUY ORDER SUBMITTED: "+str(unit)+" "+str(crypto))


def sell_crypto(crypto):
    current_price = pyupbit.get_current_price(crypto)
    unit = upbit.get_balance(ticker=crypto)
    # 매도 신호: 4시간봉 20개 동안 고가-저가 범위의 하단 20%보다 현재가가 낮음
    if current_price < get_candle_high_low_range(crypto)[3] and str(unit) != '0':
        # 시장가 매도: 매도는 몇 개 파는지로 나옴
        upbit.sell_market_order(crypto, unit)
        telegramlog("SELL ORDER SUBMITTED "+str(unit)+" "+str(crypto))


def stoploss_crypto(crypto):
    current_price = pyupbit.get_current_price(crypto)
    unit = upbit.get_balance(ticker=crypto)
    # 손절 신호: 매수가보다 10% 하락 시 손절 (매매 1회 당 총 투자금의 2% 손실까지 허용). 슬리피지 감안하여 9%에 손절선 설정
    if current_price < 0.91 * upbit.get_avg_buy_price(ticker=crypto) and str(unit) != '0':
        # 시장가 매도
        upbit.sell_market_order(crypto, unit)
        telegramlog("STOP LOSS ORDER SUBMITTED "+str(unit)+" "+str(crypto))



while True:
    try:        
        buy_crypto("KRW-BTC")
        buy_crypto("KRW-ETH")
        buy_crypto("KRW-ADA")
        buy_crypto("KRW-XRP")
        buy_crypto("KRW-SAND")
        
        sell_crypto("KRW-BTC")
        sell_crypto("KRW-ETH")
        sell_crypto("KRW-ADA")
        sell_crypto("KRW-XRP")
        sell_crypto("KRW-SAND")
        
        stoploss_crypto("KRW-BTC")
        stoploss_crypto("KRW-ETH")
        stoploss_crypto("KRW-ADA")
        stoploss_crypto("KRW-XRP")
        stoploss_crypto("KRW-SAND")
        
    except:
        print("Error! ")
        telegramlog("Bot Error!")
    
    time.sleep(1)





