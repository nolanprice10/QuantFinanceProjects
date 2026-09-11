import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, date, time, timedelta
import pandas as pd

ticker = yf.Ticker("SPY")
period = "1y"
expirations = ticker.options
today = date.today()

chain = ticker.option_chain(today)
calls = chain.calls
puts = chain.puts
print("             Call Data:          ")
print(calls[["strike", "impliedVolatility", "lastPrice"]])
print("             Put Data:           ")
print(puts[["strike", "impliedVolatility", "lastPrice"]])
callK = calls["strike"]
putK = puts["strike"]
K = callK + putK
callIV = calls["impliedVolatility"]
putIV = puts["impliedVolatility"]
IV = callIV + putIV
maturity = np.array([ (datetime.strptime(exp, "%Y-%m-%d").date() - today).days/365.0 for exp in expirations ])
x = K
y = maturity
z = IV
