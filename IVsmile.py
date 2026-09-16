import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, date, time, timedelta
import pandas as pd
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter

symbol = "SPY"
ticker = yf.Ticker(symbol)
data_today = ticker.history(period="1d")
current_price = data_today['Close'].iloc[0]
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
    calls = chain.calls[chain.calls['strike'] >= current_price]
    puts = chain.puts[chain.puts['strike'] <= current_price]
    valid_calls = calls[(calls['volume'] > 5) & (calls['impliedVolatility'] > 0.05) & (calls['impliedVolatility'] < 1.0)]
    valid_puts = puts[(puts['volume'] > 5) & (puts['impliedVolatility'] > 0.05) & (puts['impliedVolatility'] < 1.0)]
    current_K = list(valid_calls["strike"])
    current_IV = list(valid_calls["impliedVolatility"])
    num_K = len(current_K)
    repeated_maturity = [maturity_frac] * num_K
    all_K.extend(current_K)
    all_maturity.extend(repeated_maturity)
    all_IV.extend(current_IV)

x = all_K
y = all_maturity
z = all_IV

grid_x = np.linspace(min(x), max(x), 50)
grid_y = np.linspace(min(y), max(y), 50)
grid_X, grid_Y = np.meshgrid(grid_x, grid_y)
grid_Z = griddata((x, y), z, (grid_X, grid_Y), method='linear')
grid_Z = gaussian_filter(grid_Z, sigma=0.8)

plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(grid_X, grid_Y, grid_Z, cmap='viridis', edgecolor='none', alpha=0.9)
ax.set_xlabel('Strike Price')
ax.set_ylabel('Time to Maturity (Years)')
ax.set_zlabel('Implied Volatility')
plt.title(f"IV Surface for {symbol} (Current Price: {round(current_price, 2)})")
plt.show()