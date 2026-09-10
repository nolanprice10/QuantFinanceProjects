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
print(f"     Realized Volatility:   {emp_vol*100:.2f}%")
print(f"     Realized Excess Kurt:  {emp_kurt:.2f} (Fat-tail indicator)")
print(f"     Jump frequency (Lambda): {emp_lambda:.2f} shocks/year")
print(f"     Mean Jump Impact:      {emp_mu_jump*100:.2f}%")

print("\n3/4 Predict: Executing Merton Jump-Diffusion Monte Carlo...")

np.random.seed(42)
def execute_monte_carlo(returns, vol, lam, mu_j, sigma_j, ai_score, num_sims=1000, days=252):
    dt = 1/days
    mu = np.mean(returns)*days
    S0 = 100.0

    vol_scaled = vol * (1.0-0.2*ai_score)
    lam_scaled = lam * (1.0+1.5*(ai_score**2))
    mu_j_scaled = mu_j * (1.0+0.8*ai_score)
    k = np.exp(mu_j_scaled + 0.5*sigma_j**2) - 1
    drift_comp = mu-lam_scaled*k-0.5*vol_scaled**2
    paths = np.zeros((num_sims, days+1))
    paths[:, 0] = S0

    for t in range(1, days+1):
        Z = np.random.normal(0, 1, num_sims)
        n_jumps = np.random.poisson(lam_scaled*dt, num_sims)
        jump_factor = np.zeros(num_sims)
        for i in range(num_sims):
            if n_jumps[i] > 0:
                jumps = np.random.normal(mu_j_scaled, sigma_j, n_jumps[i])
                jump_factor[i] = np.sum(jumps)

        diffusion = vol_scaled*np.sqrt(dt)*Z
        paths[:, t] = paths[:, t-1]*np.exp(drift_comp*dt+diffusion+jump_factor)
    return paths

paths_current = execute_monte_carlo(log_returns, emp_vol, emp_lambda, emp_mu_jump, emp_sigma_jump, ai_score=nlp_ai_score)
paths_future = execute_monte_carlo(log_returns, emp_vol, emp_lambda, emp_mu_jump, emp_sigma_jump, ai_score=0.95)
returns_current = np.diff(np.log(paths_current), axis=1).flatten()
returns_future = np.diff(np.log(paths_future), axis=1).flatten()
kurt_current = kurtosis(returns_current, fisher=True)
kurt_future = kurtosis(returns_future, fisher=True)
var_99_current = np.percentile(returns_current, 1.0)
var_99_future = np.percentile(returns_future, 1.0)

print("         AUTONOMOUS MONTE CARLO PREDICTION OUTPUT:           ")
print("=============================================================")
print(f"{'Regime State':<28} | {'Excess Kurtosis':<18} | {'Daily 99% VaR (Tail Risk)':<20}")
print("-"*75)
print(f"{'Current Live NLP Baseline':<28} | {kurt_current:18.2f} | {var_99_current*100:19.2f}%")
print(f"{'Predicted 95% AI Saturation':<28} | {kurt_future:18.2f} | {var_99_future*100:19.2f}%")
print("=============================================================")

print("\n4/4 Render: Generating dynamic output charts...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(log_returns, color='#1f77b4', alpha=0.6, label='SPY Real Log Returns')
axes[0].set_title(f"Programmatically Ingested Market Data (10-Year SPY Returns)")
axes[0].set_xlabel("Trading Days")
axes[0].set_ylabel("Daily Returns")
axes[0].grid(True, linestyle=':', alpha=0.6)
axes[0].legend()

axes[1].hist(returns_current, bins=100, density=True, alpha=0.5, color='1f77b4', label=f'Current Live State (Kurtosis: {kurt_current:.2f})')
axes[1].hist(returns_future, bins=100, density=True, alpha=0.5, color='d62728', label=f'Predicted 95% AI Saturation (Kurtosis: {kurt_future:.2f})')
axes[1].set_yscale('log')
axes[1].set_title("Predicted Return Distribution (Log Scale - Tail Risk Focus)")
axes[1].set_xlabel("Daily Return")
axes[1].set_ylabel("Probability Density")
axes[1].legend()
axes[1].grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
plt.show()