import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

ticker = yf.Ticker("SPY")
data = ticker.history(interval="15m", period="60d")

sumPV = np.sum(data['Close'] * data['Volume'])
sumV = np.sum(data['Volume'])
vwap = sumPV/sumV

S = data['Close'].iloc[-1]
expirations = ticker.options[0]
chain = ticker.option_chain(expirations)
calls = chain.calls
puts = chain.puts

def gamma(S, K, T, r, sigma):
    from scipy.stats import norm
    if T <= 0 or sigma <= 0:
        return 0
    d1 = (np.log(S/K) + (r+0.5*(sigma**2))*T)/(sigma*np.sqrt(T))
    gamma = (norm.pdf(d1))/(S*sigma*np.sqrt(T))
    return gamma

now = datetime.now()
secPerYear = 365*24*60*60
for expK in ticker.options:
    expDate = datetime.strptime(f"{expK} 16:00:00", "%Y-%m-%d %H:%M:%S")
    secLeft = max((expDate - now).total_seconds(), 60)
    T = secLeft/secPerYear

def riskRate():
    irx = yf.Ticker("^IRX")
    rate = (irx.history(period="1d")['Close'].iloc[-1])/100.0
    return rate
r = riskRate()

K = calls['strike'].iloc[-1]

sigma = calls['impliedVolatility'].iloc[-1]

gammaValue = gamma(S, K, T, r, sigma)
OI = calls['openInterest'].iloc[-1]

GEX = gammaValue * OI * 100 * (S**2) * 0.01

vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
print(f"GEX: {GEX}")
print(f"VIX: {vix}")



