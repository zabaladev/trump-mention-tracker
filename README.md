# Trump, Family & Administration — Investment Mention Tracker

Static dashboard (GitHub Pages) tracking publicly sourced investment endorsements, buy calls, sector/theme calls and government stake announcements by Donald Trump, his family and administration officials. Each mention has a source link. Returns are shown at -30d/-7d (pre-mention), day 0, +1d/+7d/+30d/+90d and to date, vs the S&P 500 (SPY) and the Dow (DIA).

Features: client-side filters (Trump / Family / Admin, category, asset type), KPI cards, excess-return charts, a virtual $1,000-per-mention portfolio vs S&P and Dow, sector-comment baskets with a "foreshadowing" (pre-comment abnormal return) metric, an adjustable highlight threshold for big pre-moves, a disclosure-overlap panel (public OGE/SEC filings and reporting), and coverage notes listing what wasn't counted and why.

- `index.html` – self-contained dashboard
- `mentions.json` – curated, sourced mentions
- `disclosures.json` – documented holdings/trades overlaps, with sources
- `exclusions.json` – items not counted and why
- `data.json` – computed output
- `update.py` – re-fetches prices (yfinance) and regenerates `index.html` / `data.json`

Disclosure overlaps are factual timing correlations from public filings (amounts are ranges, and filings can lag trades by up to 45+ days). They are not allegations of wrongdoing.

**Not financial advice.** For informational/research purposes only. Past performance does not predict future results.

## Benchmarks & congressional trades (update)
- Every return is compared against 9 indexes: S&P 500 (^GSPC), Dow (^DJI), Nasdaq Composite (^IXIC), Nasdaq 100 (^NDX), Russell 2000 (^RUT), Russell 1000 (^RUI), Russell 3000 (^RUA), Wilshire 5000 (^W5000) and S&P MidCap 400 (^MID). Each falls back to an ETF proxy if Yahoo lacks the index. A dashboard dropdown picks the benchmark (default S&P 500). An index matrix shows win rate and average excess vs every index per group, and the portfolio chart lets you pick which index curves to show.
- `congress.json` lists congressional STOCK Act trades (House Clerk / Senate eFD, via Quiver Quantitative's public pages) in each priced mention's asset or basket components, from 30 days before to 7 days after the comment. It includes member, party, chamber, date, amount range and source. These are factual timing overlaps only. Filings lag trades by up to 30–45 days.
