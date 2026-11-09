# Quantitative Market Microstructure & Merton Jump-Diffusion Simulation Engine (Script 1)

This document details the exact data sources, ingestion protocols, parameter assumptions, and mathematical formulations implemented in **Script 1** (Real-time NLP-augmented Merton Jump-Diffusion Monte Carlo simulation).

---

## 1. Data Sources & Ingestion Protocols

* **Live Financial News Scraping:**
* **Source:** Yahoo Finance News (`[https://www.finance.yahoo.com/news](https://www.finance.yahoo.com/news)`) accessed via Python’s standard `urllib.request` library.
* **Headers & Parsing:** Employs a standard User-Agent header (`Mozilla/5.0`) to prevent blocking, parsed via `BeautifulSoup` to extract all `<title>` tags containing live article headlines.
* **Keyword Lexicon:** Scans lowercase tokenized words against a targeted quantitative/AI keyword array:
```python
keywords = ["AI", "algorothm", "algorithmic", "quant", "quantitative", "automated", "machine learning", "hft", "bot", "execution"]

```




* **Historical Price Data:**
* **Source:** Yahoo Finance API via the `yfinance` package (`yf.download`).
* **Asset:** SPY (S&P 500 ETF Trust).
* **Lookback Window:** 10 years of daily frequency (`period='10y'`, `interval='1d'`).
* **Field Selection:** Automatically prioritizes adjusted close (`'Adj Close'`) to account for dividends and splits, falling back to close (`'Close'`) if unavailable.



---

## 2. Parameter Assumptions & Mathematical Formulations

### Empirical Calibration & Merton Jump-Diffusion Model

| Parameter | Variable Name | Formula / Value | Description |
| --- | --- | --- | --- |
| **Trading Days** | `N_days` | `252` | Standard annualization convention for US equity markets. |
| **Realized Volatility** | `sigma_emp` | `std(R_log) * sqrt(252)` | Annualized standard deviation of daily log returns (`R_log = ln(P_t / P_t-1)`). |
| **Excess Kurtosis** | `K_emp` | `scipy.stats.kurtosis(..., fisher=True)` | Fisher excess kurtosis measuring fat-tail departure from normality. |
| **Jump Threshold** | `J_thresh` | `2.5 * std(R_log)` | Statistical cutoff filter identifying extreme return shocks. |
| **Jump Frequency** | `lambda` | `(Count(abs(R_log) > J_thresh) / N_total) * 252` | Annualized Poisson intensity of market shocks. |
| **Mean Jump Impact** | `mu_j` | `mean(J_filtered)` (default: `-0.02`) | Expected log-return magnitude per jump event. |
| **Jump Volatility** | `sigma_j` | `std(J_filtered)` (default: `0.02`) | Dispersion of jump impact sizes. |

### AI Sentiment Impact Scaling Rules

The dynamic sentiment score (`ai_score`) bounded between `0.50` and `0.95` modifies baseline parameters to simulate increased automation stress:

* **Volatility Scaling:**
`sigma_scaled = sigma * (1.0 - 0.2 * ai_score)`
* **Jump Frequency Scaling:**
`lambda_scaled = lambda * (1.0 + 1.5 * (ai_score ** 2))`
* **Mean Jump Impact Scaling:**
`mu_j_scaled = mu_j * (1.0 + 0.8 * ai_score)`
* **Compensating Drift & Jump Term:**
* Expected jump relative change:
`k = exp(mu_j_scaled + 0.5 * sigma_j**2) - 1`
* Drift component:
`drift_comp = mu - lambda_scaled * k - 0.5 * sigma_scaled**2`
