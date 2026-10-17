# Trump, Family & Administration: Investment Mention Tracker
### An open experiment: does public data show patterns consistent with insider trading or market manipulation?

**Live dashboard:** https://zabaladev.github.io/trump-mention-tracker/

> **Disclaimer.** This is an independent research and educational project. It is **not legal advice and not financial advice**. Everything here comes from public sources. A timing overlap, a large pre-announcement price move, or a disclosed trade near a public comment is **not evidence of wrongdoing**. Lawful explanations (public news, sector momentum, pre-planned trades, blind/managed accounts, chance) are common. The project does not accuse any person or organization of breaking any law. Only regulators and courts can make those determinations. **Corrections are welcome. Please open an issue** with a source.

---

## 1. Purpose & hypotheses

Senior public officials and people close to them sometimes publicly promote specific stocks, coins, sectors, or companies in which the government takes a stake. This project collects those statements and tests, with public market and disclosure data, whether the observable patterns are **consistent with** the concerns that U.S. insider-trading, conflict-of-interest and anti-manipulation rules are designed to address. "Consistent with" means a pattern worth explaining. It does not mean a finding of a violation.

Working hypotheses (each can be rejected by the data):

| # | Hypothesis | What would be consistent with it | Where to look |
|---|---|---|---|
| H1 | Public promotion moves prices | Abnormal return on day 0 / +1d after a mention | KPI cards, "excess return by horizon" chart |
| H2 | Information reaches markets **before** the comment | Abnormal returns in the −30d / −7d windows that end before the comment | "Pre-comment moves" panel, sector "foreshadowing" metric |
| H3 | People with disclosure obligations, or linked entities, hold or trade promoted assets around promotion dates | Disclosed holdings/trades near mention dates | "Disclosure overlap" panel |
| H4 | Members of Congress trade the promoted asset just before the comment | STOCK Act trades in the 30 days before a mention | "Congressional STOCK Act trades" panel |
| H5 | Some individuals/funds outperform peers and benchmarks unusually | Persistent risk-adjusted outperformance vs comparable peers | Planned peer ranking (see §5) |
| H0 (null) | Promoted assets behave like any other asset, and overlaps occur at the rate chance predicts | Excess returns ≈ 0, overlap rates match random-date baselines | Significance section (§4.4) |

## 2. The legal framework, in brief

These are plain-language summaries for context, linked to official texts. They are not legal interpretations. Several rules apply only to certain people (see the notes).

- **STOCK Act of 2012** (Stop Trading on Congressional Knowledge Act, Pub. L. 112-105). It affirms that Members of Congress, congressional staff, and executive-branch employees are **not exempt** from insider-trading laws and owe a duty of trust and confidence regarding nonpublic information they learn through their positions. It also requires **periodic transaction reports** for securities trades over $1,000, filed within 30 days of notice and no later than 45 days after the trade. Source: [congress.gov – S.2038](https://www.congress.gov/bill/112th-congress/senate-bill/2038). Filings: [House Clerk](https://disclosures-clerk.house.gov/FinancialDisclosure), [Senate eFD](https://efdsearch.senate.gov/search/).
- **Ethics in Government Act of 1978** (Pub. L. 95-521, now codified at 5 U.S.C. ch. 131). It created public financial disclosure for senior officials, including the President and Vice President: annual OGE Form 278e reports and 278-T periodic transaction reports. Sources: [congress.gov – S.555 (95th)](https://www.congress.gov/bill/95th-congress/senate-bill/555), [5 U.S.C. ch. 131](https://uscode.house.gov/view.xhtml?path=/prelim@title5/part4/chapter131&edition=prelim), [5 CFR part 2634 (disclosure rules)](https://www.ecfr.gov/current/title-5/chapter-XVI/subchapter-B/part-2634), [OGE](https://www.oge.gov/), [OGE disclosure search](https://extapps2.oge.gov/web/OGE.nsf/Officials%20Individual%20Disclosures%20Search%20Collection?OpenForm).
- **OGE Standards of Ethical Conduct, 5 CFR part 2635.** These cover executive-branch employees: no use of public office for private gain, **no endorsement of products, services or enterprises** in an official capacity (§2635.702), and limits on using nonpublic information (§2635.703). *Note: the President and Vice President are excluded from the part's definition of "employee."* Source: [eCFR 5 CFR 2635](https://www.ecfr.gov/current/title-5/chapter-XVI/subchapter-B/part-2635).
- **18 U.S.C. § 208 (criminal conflict of interest).** It bars executive-branch employees from participating personally and substantially in particular matters affecting their own financial interests or those of their spouse, minor child, or certain affiliated organizations. *Note: 18 U.S.C. § 202(c) makes § 208 inapplicable to the President and Vice President.* Sources: [18 U.S.C. § 208](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title18-section208&num=0&edition=prelim), [§ 202](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title18-section202&num=0&edition=prelim).
- **SEC Rule 10b-5** (Securities Exchange Act §10(b)). It prohibits fraud and manipulation in connection with the purchase or sale of securities. This is the basis of insider-trading liability, including the "misappropriation" theory. Rule 10b5-2 describes duties of trust and confidence. Sources: [17 CFR 240.10b-5](https://www.ecfr.gov/current/title-17/section-240.10b-5), [17 CFR 240.10b5-2](https://www.ecfr.gov/current/title-17/section-240.10b5-2), [SEC adopting release (2000)](https://www.sec.gov/rules-regulations/2000/08/selective-disclosure-insider-trading).
- **Commodity Exchange Act §6(c)(1) and CFTC Rule 180.1.** These prohibit manipulative and deceptive devices, including misappropriation-based insider trading, in commodities, futures and swaps. That covers crypto-linked derivatives, oil futures and similar instruments. Source: [17 CFR 180.1](https://www.ecfr.gov/current/title-17/section-180.1).
- **Event contracts / prediction markets.** On Feb 25 2026 the CFTC Division of Enforcement issued an advisory stating it can pursue insider trading in event contracts on registered exchanges under §6(c)(1) and Rule 180.1. Sources: [CFTC press release 9185-26](https://www.cftc.gov/PressRoom/PressReleases/9185-26), [advisory PDF](https://www.cftc.gov/media/13351/Enf_AdvisoryKalshi022526/download), [CRS Legal Sidebar LSB11406](https://www.congress.gov/crs_external_products/LSB/PDF/LSB11406/LSB11406.1.pdf). *Context only: this tracker does not currently analyze prediction-market data.*

What public data **can't** establish: whether someone had material nonpublic information, owed a duty, or traded *because* of it. Those are core legal elements. This project can only flag patterns.

## 3. Data

- `mentions.json`: hand-curated public statements by Donald Trump, family members, and administration officials that promote an asset, company, sector or government stake. Each has a date, quote/summary, category, group (Trump / Family / Admin) and a source URL. Sector/theme calls (e.g. rare earths/"magnets") map to a documented equal-weight **basket** of related tickers.
- `exclusions.json`: candidates considered but not scored (private companies, no price data, too generic) and why.
- `disclosures.json`: documented holdings/trades by speakers, spouses, family-linked entities and officials from public filings (OGE 278e/278-T, SEC 13D/13G/Form 4/8-K/S-1) and credible reporting.
- `congress.json`: congressional STOCK Act trades in the mentioned asset (or basket components) from 30 days before to 7 days after each mention. Data comes from official House/Senate filings as compiled by Quiver Quantitative, with a direct House PTR where Quiver was incomplete.
- Prices come from Yahoo Finance via `yfinance`: daily closes, adjusted for splits and dividends.

## 4. Methodology

### 4.1 Event windows
Entry = close on the mention day (or the next trading day). Windows: **−30d, −7d** (ending at the prior close, so they exclude the reaction), **day 0** (prior close → mention-day close), and **+1d, +7d, +30d, +90d, to date** (calendar days from entry).

### 4.2 Abnormal ("excess") returns & benchmarks
Excess return = asset return − benchmark return over the identical window. Nine benchmarks are selectable: S&P 500 (^GSPC, default), Dow (^DJI), Nasdaq Composite (^IXIC), Nasdaq 100 (^NDX), Russell 2000/1000/3000 (^RUT/^RUI/^RUA), Wilshire 5000 (^W5000), S&P MidCap 400 (^MID). Each falls back to an ETF if the index is unavailable. Crypto also shows excess vs BTC. *Simple market-adjusted model; no beta adjustment yet.*

### 4.3 Pre-move / "foreshadowing"
A mention is flagged when its −30d or −7d excess return passes a threshold you set (default 10%). For sector calls, the basket's pre-comment abnormal return is the "foreshadowing" metric. Flags mark correlation only.

### 4.4 Significance (current, simple)
These are one-sample t-statistics and 5,000-draw bootstrap 95% CIs on mean excess vs the S&P 500 (computed 2026-10-17). They are indicative only, because events overlap in time and samples are small.

| Group | +30d n | +30d mean excess (95% CI) | t | To-date mean excess (95% CI) | t |
|---|---|---|---|---|---|
| All | 55 | −1.7% (−9.0, +5.9) | −0.44 | −24.4% (−42.8, −4.1) | −2.46 |
| Trump | 28 | +2.7% (−5.2, +10.6) | 0.66 | +5.1% (−21.8, +36.2) | 0.33 |
| Family | 19 | −13.4% (−26.3, −1.9) | −2.10 | −71.4% (−87.5, −53.6) | −8.07 |
| Admin | 8 | +10.9% (−13.5, +39.6) | 0.74 | −27.0% (−51.2, −5.2) | −2.16 |

Pre-comment (−30d) mean excess across all priced mentions: +8.5%, median −0.1%, t = 0.92. That is **not statistically distinguishable from zero**. A few large outliers drive the mean. Planned: random-date placebo tests, beta-adjusted abnormal returns, and clustering corrections.

### 4.5 Disclosure & congressional overlaps
For each mention we list any documented holding or trade in the same asset by the speaker, spouse, family-linked entity or official, plus any congressional trade from −30d to +7d. We record member, party, chamber, trade date, days relative to the comment, type, amount range and source link.

### 4.6 Virtual portfolio
The portfolio puts $1,000 in each mentioned asset at entry, either held to date or sold after 30 days. It's compared with the same cash flows invested in the selected index(es).

## 5. Measuring "outperformance" of individuals & funds

**Current:** performance is measured per *mention group* (Trump / Family / Admin) vs nine indexes: win rate, share beating the index, mean/median excess, and portfolio vs index.

**Planned peer-outperformance ranking (not yet built):** for each disclosing individual (Members of Congress, senior officials with 278-T filings) and linked fund/entity with public holdings (13F/13D):
1. Reconstruct trade-level returns from disclosed dates and amount-range midpoints, at +30/+90/+180 days.
2. Compare each person to **peers** (same chamber/party/committee; or same fund style) and to benchmarks, using risk-adjusted metrics (alpha vs a market or factor model, information ratio, hit rate).
3. Test persistence and significance with placebo dates and multiple-comparison control, because with thousands of filers some will look exceptional by chance.
4. Publish rankings only as statistical outliers with caveats, never as accusations.

Results will appear on the [dashboard](https://zabaladev.github.io/trump-mention-tracker/) as they are built.

## 6. Current high-level findings (neutral, as of 2026-10-17)

See the live dashboard for exact, filterable numbers.
- **Family-promoted assets have underperformed.** $1,000 in each of the 19 priced family-promoted assets (10 family-linked company stocks and 9 crypto tokens or coins) would be worth about half its cost today, far behind the indexes. This is the only group whose underperformance is statistically clear at +30d.
- **Trump's own mentions roughly track the market.** A small positive average excess, not statistically significant. A few large winners (e.g. Dell after the Feb 2026 mention) drive results.
- **Admin officials' mentions** (8 priced) trail the index to date, with wide uncertainty.
- **All mentions combined:** a $1,000-per-mention portfolio is about flat (−1%) vs about +24% for the same cash in the S&P 500. About 4 in 10 mentions beat the S&P 500 one month later.
- **Day-0 reactions are large for newly launched tokens.** The median mention-day move is about +4.6%, and the mean is much higher because of launch-day jumps.
- **Timing overlaps exist and are documented:**
  - 35 mentions involve an asset that the speaker, family or a linked entity has publicly disclosed holding or trading.
  - 66 congressional trades (59 before the comment) fall in the −30d/+7d windows of 13 mentions. Most are small ($1K–$15K), and they include both buys and sells.
  - These counts are not compared with a chance baseline yet.

## 7. Limitations

- **Disclosure lags and ranges.** STOCK Act/OGE filings arrive up to 30–45+ days after trades and report dollar ranges, not exact amounts or prices. Late or amended filings are common.
- **Chance overlaps.** Members of Congress disclose tens of thousands of trades, and popular large-caps (NVDA, AAPL, TSLA) are traded constantly. Some overlap with any date is expected; without a random-date baseline, overlap counts mean little.
- **Selection bias.** Mentions are curated from what is findable and promotional, so statements may be missed and memorable calls over-represented. Search coverage of video and speeches is incomplete.
- **Small, overlapping samples.** Many mentions cluster in the same weeks (e.g. April 2025), so they aren't independent.
- **Data gaps.** No intraday prices (the minute-level timing of posts isn't captured). The nine index benchmarks are price-only, while assets are total-return; four dividend-reinvested ETF benchmarks (SPY, DIA, QQQ, VTI) give a like-for-like comparison. Crypto, futures and private companies lack congressional/OGE coverage. Third-party compilations (Quiver) can miss filings. Family-member and spouse disclosures are only partly public.
- **Causation.** Price moves can reflect news, momentum, earnings or chance. Nothing here identifies *why* anyone traded.

## 8. Repository

- `index.html`: self-contained dashboard (Chart.js inlined; all filtering client-side)
- `template.html` + `update.py`: re-fetch prices and regenerate `index.html` / `data.json`
- `mentions.json`, `exclusions.json`, `disclosures.json`, `congress.json`: curated, sourced inputs
- `data.json`: computed output · `publish.sh`: rebuild + allow-listed publish steps

Dashboard extras: a benchmark selector, an index matrix (win rate / mean excess vs every index per group), selectable index lines on the portfolio chart, a ticker lookup, sector baskets, "What should I take from this?" and plain-English insights sections, and coverage notes.

## 9. Corrections & contributions

Found an error, a missing statement, a mis-mapped ticker, or a filing we overlooked? **Open an issue** with a link to the primary source. Corrections are published in the commit history.

**Not legal or financial advice. Overlaps are not evidence of wrongdoing. Past performance does not predict future results.**
