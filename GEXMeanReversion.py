import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

API_KEY = "PKWSO3J44J5XNRV4N2B7LISHCN"
API_SECRET = "ZPfES9YxHZuQHFMm15wo2Wc69Ks9rd5mtCwzj8ECCDH"
client = TradingClient(API_KEY, API_SECRET, paper=True)
print("Connected to Alpaca account:")
account = client.get_account()

ticker = yf.Ticker("SPY")
data = ticker.history(period="5d")

sumPV = np.sum(data['Close'] * data['Volume'])
sumV = np.sum(data['Volume'])
vwap = sumPV/sumV

S = data['Close'].iloc[-1]
expirations = ticker.options[0]
if expirations: 
    chain = ticker.option_chain(expirations[0])
    calls = chain.calls


    def gamma(S, K, T, r, sigma):
        from scipy.stats import norm
        if T <= 0 or sigma <= 0:
            return 0
        d1 = (np.log(S/K) + (r+0.5*(sigma**2))*T)/(sigma*np.sqrt(T))
        gamma = (norm.pdf(d1))/(S*sigma*np.sqrt(T))
        return gamma

    now = datetime.now()
    secPerYear = 365*24*60*60

    expDate = datetime.strptime(f"{expirations[0]} 16:00:00", "%Y-%m-%d %H:%M:%S")
    secLeft = max((expDate - now).total_seconds(), 60)
    T = secLeft/secPerYear

    try:
        irx = yf.Ticker("^IRX")
        r = (irx.history(period="1d")['Close'].iloc[-1])/100.0
    except:
        r = 0.04

    K = calls['strike'].iloc[-1]
    sigma = calls['impliedVolatility'].iloc[-1]
    gammaValue = gamma(S, K, T, r, sigma)
    OI = calls['openInterest'].iloc[-1]
    GEX = gammaValue * OI * 100 * (S**2) * 0.01
else:
    GEX =0

vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
print(f"Price: {S} | VWAP: {vwap} | GEX: {GEX} | VIX: {vix}")

signal = 0
if S > vwap and GEX > 0 and vix < 15:
    signal = 1
elif S < vwap and GEX > 0 and vix < 15:
    signal = -1
else:
    signal = 0

print(f"Signal: {signal}")