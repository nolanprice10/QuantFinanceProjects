import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, date
import pandas as pd

ticker = yf.Ticker("SPY")
period = "1y"
expirations = ticker.options

chain = ticker.option_chain(expirations[0])
calls = chain.calls
puts = chain.puts
print("             Call Data:          ")
print(calls[["strike", "impliedVolatility", "lastPrice"]])
print("             Put Data:           ")
print(puts[["strike", "impliedVolatility", "lastPrice"]])
