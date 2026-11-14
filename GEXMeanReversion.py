import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

ticker = yf.Ticker("SPY")
data = ticker.history(start="2024-01-01", end="2026-01-01")

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

K = calls['strike'].values

sigma = calls['impliedVolatility'].values

gammaValue = gamma(S, K.values, T, r, sigma.values)
OI = calls['openInterest'].values

GEX = gammaValue * OI * 100 * (S**2) * 0.01

vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
print(f"GEX: {GEX}")
print(f"VIX: {vix}")

data["marketReturn"] = data["Close"].pct_change()

data["VWAP"] = (data["Close"] * data["Volume"]).cumsum() / data["Volume"].cumsum()
data["GEX"] = gammaValue * OI * 100 * (data["Close"]**2) * 0.01
data["VIX"] = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]

data["Signal"] = 0
data.loc[(data["Close"] > data["VWAP"]) & (data["GEX"] > 0) & (data["VIX"] < 15), "Signal"] = 1
data.loc[(data["Close"] < data["VWAP"]) & (data["GEX"] > 0) & (data["VIX"] < 15), "Signal"] = -1
data.loc[(data["Close"] == data["VWAP"]) | (data["GEX"] <=0) | (data["VIX"] > 15), "Signal"] = 0

data["strategySignal"] = data["Signal"].shift(1)
data["strategyReturn"] = data["marketReturn"] * data["strategySignal"]
data["marketCumulative"] = (1 + data["marketReturn"].fillna(0)).cumprod()
data["strategyCumulative"] = (1 + data["strategyReturn"].fillna(0)).cumprod()

print(f"Total Market Return: {(data['marketCumulative'].iloc[-1] - 1)*100:.2f}")
print(
    f"Total Strategy Return: {(data['strategyCumulative'].iloc[-1] - 1)*100:.2f}%"
)