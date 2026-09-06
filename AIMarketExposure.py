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