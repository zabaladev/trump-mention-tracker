# Trump Family Investment Mention Tracker

Static dashboard tracking publicly sourced investment endorsements/promotions by Donald Trump and family members (47 mentions, each with a source link), with asset returns at -7d/-1d/+1d/+7d/+30d/+90d/to-date vs SPY (stocks) or BTC (crypto), win rates, group patterns, and a virtual $1,000-per-mention portfolio.

- `index.html` – self-contained dashboard (Chart.js inlined)
- `mentions.json` – curated, sourced mentions
- `data.json` – computed returns/stats
- `update.py` – re-fetches prices (yfinance) and regenerates `index.html` / `data.json` (`pip install yfinance pandas && python update.py`)

Data: Yahoo Finance via yfinance. Some mentions lack price data (private/delisted assets).

**Not financial advice.** For informational/research purposes only; past performance does not predict future results.
