# Crypto Sentiment & Trader Performance Analysis

> Exploring the relationship between the Bitcoin Fear/Greed Index and trader behaviour on Hyperliquid perpetual futures — Jan 2023 to May 2025.

---

## Overview

This project analyses **167,857 perpetual futures trades** from Hyperliquid, cross-referenced against the daily **Bitcoin Fear & Greed Index**, to answer a core question:

**Does market sentiment predict trader profitability — and do top traders behave differently across sentiment regimes?**

The analysis uncovers hidden patterns in win rates, position sizing, directional bias, and fee drag across five sentiment regimes: Extreme Fear, Fear, Neutral, Greed, and Extreme Greed.

---

## Datasets

| Dataset | Source | Records |
|---|---|---|
| Historical Trader Data | Hyperliquid Perpetuals | 211,224 raw trades |
| Bitcoin Fear/Greed Index | Alternative.me | 2,644 daily records (2018–2025) |
| Merged dataset | Date-joined | 167,857 trades (Jan 2023 – May 2025) |

---

## Key Findings

### 1. Extreme Greed is the most profitable regime
- **$73.14 avg PnL/trade** — highest of all regimes
- **45.9% win rate** — also the highest
- **Only 1.02% fee drag** — the most cost-efficient regime

### 2. The contrarian strategy is confirmed
| Regime | Best Side | Avg PnL |
|---|---|---|
| Extreme Fear | BUY (long) | $91.78 |
| Fear | BUY (long) | $84.33 |
| Neutral | SELL (short) | $46.32 |
| Greed | SELL (short) | $62.53 |
| Extreme Greed | SELL (short) | $125.19 |

Buying during fear and shorting during greed is the single most consistent edge in the dataset.

### 3. Win rate is a misleading metric
The top trader earned **$1.95M with only a 32.4% win rate**. Another made $273K winning just 19% of trades. Success comes from **asymmetric payoffs**, not accuracy.

### 4. Position sizing separates top from bottom traders
- Top traders deploy **$9,764 avg** during Greed periods
- Bottom traders deploy **$2,203 avg** during the same periods — a **4.4x gap**
- Both groups trade contrarian at nearly identical rates (41.4% vs 39.5%), confirming that **direction alone is not the edge**

### 5. Overtrading during Greed is costly
Fee drag peaks at **3.78% of PnL during Greed** — nearly 4x higher than during Extreme Greed (1.02%). High-frequency churning during euphoric markets silently destroys returns.

---

## Strategy Scorecard

| Regime | Avg PnL | Win Rate | Best Side | Fee Drag | Recommended Action |
|---|---|---|---|---|---|
| Extreme Fear | $47.45 | 39.1% | BUY | 1.46% | Selective long |
| Fear | $56.54 | 38.8% | BUY | 2.29% | Go long |
| Neutral | $33.41 | 40.9% | SELL | 2.84% | Reduce size |
| Greed | $34.60 | 39.8% | SELL | 3.78% | Short bias |
| Extreme Greed | $73.14 | 45.9% | SELL | 1.02% | Aggressively short |

---

## Project Structure

```
crypto-sentiment-analysis/
├── crypto_analysis.py         # Full analysis code (data cleaning, merging, EDA)
├── crypto_sentiment_report.pdf  # Final PDF report with charts and insights
└── README.md                  # This file
```

---

## How to Run

### Prerequisites
```bash
pip install pandas matplotlib reportlab
```

### Steps

1. Download both datasets and place them in the same folder as `crypto_analysis.py`
2. Update the file paths at the top of the script:
```python
trader_df    = pd.read_csv("historical_trader_data.csv")
sentiment_df = pd.read_csv("fear_greed_index.csv")
```
3. Run the script:
```bash
python crypto_analysis.py
```

The script will output all analysis results to the console. To regenerate the PDF report, use the `build_report.py` section at the bottom.

---

## Methodology

- **Sentiment labels** created using `pd.cut` on the Fear/Greed index value:
  - Extreme Fear: 0–24 | Fear: 25–44 | Neutral: 45–55 | Greed: 56–74 | Extreme Greed: 75–100
- **Merge key**: trades joined to sentiment index by date (extracted from `Timestamp IST`)
- **Win rate**: % of trades where `Closed PnL > 0`
- **Contrarian score**: % of trades that are BUY during Fear/Extreme Fear OR SELL during Greed/Extreme Greed
- **Fee drag**: Total fees / Total PnL per regime

---

## Tools Used

- **Python** — pandas, matplotlib
- **ReportLab** — PDF report generation
- **Data range** — January 2023 to May 2025

---

## Report

The full PDF report (`crypto_sentiment_report.pdf`) includes:
- Executive summary with key metrics
- PnL performance charts by sentiment regime
- Long vs short directional analysis
- Top 10 vs Bottom 10 trader behaviour comparison
- Fee drag analysis
- 6 actionable trading strategy recommendations
- Methodology appendix

---

*This analysis was conducted for educational purposes. Past performance does not guarantee future results.*
