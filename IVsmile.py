import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, date, time, timedelta
import pandas as pd

ticker = yf.Ticker("SPY")
period = "1y"
expirations = ticker.options
today = date.today()
all_K = []
all_maturity = []
all_IV = []

for exp in expirations:
    expiry_date = datetime.strptime(exp, "%Y-%m-%d").date()
    days_to_maturity = (expiry_date - today).days
    maturity_frac = days_to_maturity / 365.0

    chain = ticker.option_chain(exp)
    calls = chain.calls
    current_K = list(calls["strike"])
    current_IV = list(calls["impliedVolatility"])
    num_K = len(current_K)
    repeated_maturity = [maturity_frac] * num_K
    all_K.extend(current_K)
    all_maturity.extend(repeated_maturity)
    all_IV.extend(current_IV)

x = all_K
y = all_maturity
z = all_IV

plt.figure()
ax = plt.axes(projection='3d')
ax.scatter(x, y, z)
ax.set_xlabel('Strike Price')
ax.set_ylabel('Time to Maturity (Years)')
ax.set_zlabel('Implied Volatility')
plt.title("IV Smile")
plt.show()
plt.savefig('IV_smile.png')