import numpy as np
import matplotlib as plt
import re
import urllib.request
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from scipy.stats import kurtosis

print("1/4 Scrape and Ingest: Fetching live financial news for AI NLP analysis.")
keywords = [
    "AI", "algorothm", "algorithmic", "quant", "quantitative", "automated", "machine learning", "hft", "bot", "execution",
]

def scrape_ai_score():
    url = "https://www.finance.yahoo.com/news"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        html = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(html, "html.parser")
        headlines = [item.text.lower() for item in soup.find_all("title")]
        full_text = " ".join(headlines)
        words = re.findall(r'\w+', full_text)
        if not words:
            return 0.70
        ai_count = sum(1 for word in words if word in keywords)
        density = ai_count / len(words)
        dynamic_score = min(max(density*25.0+0.50, 0.50), 0.95)
        print(f"   -> Extracted {len(headlines)} headlines ({len(words)} words).")
        print(f"   -> found {ai_count} AI-related words.")
        print(f"   -> AI Impact Score: {dynamic_score*100:.2f}%")
        return dynamic_score
    except Exception as e:
        print(f"   -> Error occurred: {e}")
        return 0.72

nlp_ai_score = scrape_ai_score()

print("\n2/4 Ingest & Calibrate: Fetching 10 years of data...")
ticker = "SPY"
df = yf.download(ticker, period='10y', interval='1d', progress=False)

if 'Adj Close' in df.columns:
    prices = df['Adj Close']
else:
    prices = df['Close']

log_returns = np.log(prices/prices.shift(1)).dropna().values.flatten()

trading_days = 252
emp_vol = np.std(log_returns)*np.sqrt(trading_days)
emp_kurt = kurtosis(log_returns, fisher=True)

jump_threshold = 2.5*np.std(log_returns)
jumps = log_returns[np.abs(log_returns)>jump_threshold]

emp_lambda = (len(jumps)/len(log_returns))*trading_days
emp_mu_jump = np.mean(jumps) if len(jumps) > 0 else -0.02
emp_sigma_jump = np.std(jumps) if len(jumps) > 0 else 0.02

print("     -> Empirical Microstructure metrics Computed:")
print(f"     Total Data Points:     {len(log_returns)} trading days")
print(f"     Realized Volatility:     {emp_vol*100:.2f}%")
print(f"     Realized Excess Kurt:     {emp_kurt:.2f} (Fat-tail indicator)")
print(f"     Jump frequency (Lambda):     {emp_lambda:.2f} shocks/year")
print(f"     Mean Jump Impact:     {emp_mu_jump*100:.2f}%")