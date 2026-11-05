# IMPROVEMENTS backlog (prioritized)
For future autonomous improvement runs. Keep everything sourced, never fabricate, and never publish `private/`.

## ⚠️ Design system v2 (2026-10-17): every future run MUST follow this
The dashboard was redesigned because it had become one long, dense page (about 49,000 px on desktop). Do not add new clutter. Rules:
1. **Tabs, not one long page.** Put new content in the right tab: **Overview** (hero, plain-English takeaway, insights, newest, best/worst, only short items), **Mentions** (ticker lookup, all-mentions table, timeline, sector baskets, coverage notes), **Performance** (headline cards, portfolio and excess charts, group table, each-mention chart, then folded advanced stats), **Disclosures & Congress** (congressional trades, disclosure overlaps, family-linked companies, Truth API, pre-moves), **Rankings** (peer-outperformance ranking), **Methods** (how-to-read guide, glossary, data and limitations, section map, feeds, links). Never add a seventh tab without a strong reason.
2. **Progressive disclosure.** Anything advanced (luck tests, robustness checks, method notes, long tables) goes inside `<details class="more"><summary>Plain title</summary><div class="morein">…</div></details>`, collapsed by default. Explanatory text over about 360 characters is clamped automatically to 3 lines with "Read more" (`clampLong()` in design.js), so lead with the conclusion in the first sentence.
3. **Overview stays short.** At most 4 hero numbers (`heroK()`), one takeaway paragraph, and insights showing 4 by default. Do not add panels to Overview. Add an insight sentence instead, or put the panel in another tab.
4. **Tokens only.** Use CSS variables (`--bg --pn --pn2 --bd --tx --tx2 --mu --mu2 --ink --g --r --link --acc --hl`). Never hard-code colours for text/backgrounds (light and dark themes must both work). In charts use `CV('--mu')`, `INK()` etc. Keep the fixed who-colours and shapes: Trump amber ●, Family violet ▲, Admin cyan ◆.
5. **Charts:** fewer, larger. Create them with `mk(id,cfg)` inside `render()` (so they redraw when a tab opens). Charts in hidden tabs or folded sections are redrawn on tab switch / details toggle. Give every canvas a fixed-height wrapper and an `aria-label`.
6. **Tables:** wrap them in `<div style="overflow-x:auto">` (gets the 72vh internal scroll, sticky header and first column on mobile). Don't let a table make the page taller than one screen.
7. **Navigation & URLs:** `goSec(id)` switches to the right tab and opens folded sections. Add new section ids to the section list `S` (it feeds the Methods "All sections" map and the "Jump to a section" menu). Tabs use `#overview`…`#methods` hashes; filters stay in `?who=…&bm=…`; `#ticker=XYZ` opens the Mentions tab.
8. **Mobile first:** check 390px width every run (check.py does). No horizontal page scroll; filter bar must stay compact (primary filters visible, the rest under "More filters").
9. **Screenshots:** after visible changes run `python shots.py` and publish `screens/latest-desktop.png` and `screens/latest-mobile.png` (as `.png.b64`; the screens workflow decodes them).

## P0: data correctness & coverage
1. **Congressional trades completeness.** Quiver missed Greene's Apr 8–9 2025 House PTR. Cross-check every window against House Clerk PTR XML (disclosures-clerk.house.gov) and Senate eFD directly, plus Capitol Trades. Also add trades by members no longer in the current-legislators list.
2. **Recurring mention discovery.** Run X searches (realDonaldTrump, DonaldJTrumpJr, EricTrump, LaraLeaTrump, family venture accounts) and Truth Social / whitehouse.gov remarks weekly. Dedupe against mentions.json.
3. **Admin officials coverage.** Systematically review Lutnick, Bessent, Navarro, Burgum, Wright, Hassett and Commerce/DoD announcements of new equity stakes (e.g. Vulcan Elements, private deals → note in exclusions).
4. **Total-return benchmarks.** DONE 2026-10-17 03:30 UTC: SPY/DIA/QQQ/VTI dividend-adjusted benchmarks (`*_tr` keys) + insight + glossary. Next: optional IWM/IWB/IWV/MDY TR proxies, or a single price/TR toggle instead of extra columns if the matrix gets too wide on mobile.
5. **Intraday reaction.** Free daily data can't show minute-level moves for after-hours/intraday posts. Consider Polygon/Alpaca free tiers for 1-min bars around post timestamps (store post timestamps in mentions.json).
6. **OGE 278-T automation.** Parse new Trump/family/official periodic transaction reports for tickers in mentions.json (trumptrack.app shows ~3.6K Q1 2026 trades, a large gap vs our curated disclosures.json).

## P1: analysis features
7. **Sentiment / negative mentions.** Track attacks and criticism too (e.g. tariff threats on named companies) as a separate "Company criticism" / Negative category, with short-side stats. PROGRESS 2026-10-17: first entry GOOGL Sep 14 Finland permitting criticism. Next: short-side / stance-aware portfolio (#12b) and more verified criticism leads from trumpstonks.
8. **Statistical significance.** DONE 2026-10-17 for the filtered set (bootstrap 95% range + sign test + verdict). Per-group grid + multiple-testing caveat DONE 2026-10-17. Benjamini-Hochberg adjusted verdict on the group grid DONE 2026-10-17 ~03:55 UTC (bootstrap p via `boot().p`, `bh()`). BH on the sector panel's 5 windows DONE 2026-10-17 ~04:35 UTC (`tR`/`adjC` in secPanel). Per-category grid with its own BH adjustment DONE 2026-10-17 ~04:55 UTC (`sigCats`, `#tSigC`, categories with n≥5). BH across the by-sector table DONE 2026-10-17 ~05:00 UTC (`SG`/`SC`/`sMk`, `#secBP`; sectors with n≥5 per window; 7 checks, none survive). Next: industry-level peers (#12e) so groups get bigger, or a beta-adjusted version (#9).
9. **Event-overlap control.** PROGRESS 2026-10-17 ~05:05 UTC: beta-adjusted (market-model, no alpha) abnormal returns vs S&P 500 DONE (`beta`/`abn` per row in data.json, `#secBeta` panel, BH column). Next: clustered/non-overlapping-sample significance, and an optional toggle to show beta-adjusted numbers in the main cards. Many mentions cluster (e.g. Apr 2025). Add de-duplicated / non-overlapping sample stats and a market-model (beta-adjusted) abnormal return.
10. **Per-ticker pages.** Permalinks DONE 2026-10-17 (`#ticker=DELL`, table links). Lookup price chart with mention markers and scaled index line DONE 2026-10-17 (weekly). Daily close-up around each mention DONE 2026-10-17 ~11:20 UTC (`zoom` calendar + `zm` per row, `tkZoom()`, `#tkZW`/`#tkZs`/`#tkZN`; −30/+60 sessions, both lines from 0% at the prior close). Sector-ETF overlay DONE via #12e. Industry fund line on the close-up DONE 2026-10-17 ~11:30 UTC (`zm.f/fk/fv`, peer ETF else SPDR sector; caption sentence). Next: trim `zoom.bench` to fewer indexes if page size matters (#17).
11. **Sector baskets.** Allow cap-weighted vs equal-weight toggle, and document each basket component's source.
12. **Prediction-market context (public).** Kalshi/Polymarket odds around policy announcements (aggregate only).

12b. **Stance-aware long/short backtest** (idea from trumpstonks.com): $1 long on positive mentions, $1 short on negative, plus "edge vs a long-only baseline of the same stock". Depends on #7. DONE 2026-10-17 ~09:00 UTC as the "Praise vs criticism" panel (`stancePanel`, `#secStance`, table `#tSt`; follow-the-tone vs bet-for-every-stock per window, dedup-aware). Next: add a portfolio line for follow-the-tone once #7 has 5+ criticisms, and an insights bullet then.
12c. **Mention backfill from trumpstonks.com** (lists ~1,415 verbatim Trump company mentions Jan 2025 to Oct 16 2026). Verify each against the original Truth Social/WH source before adding. PROGRESS 2026-10-17: added BA (Oct 1), BDX (Oct 5), GFS (Oct 14), **LMT (Sep 21)**. Scout 2026-10-17 evening: (a) Intel line inside the Oct 14 GFS post is a *retrospective reference* to the prior Intel stake ("As I showed with our massive WIN with INTEL") — INTC already has 3 tracked mentions; do **not** add a duplicate day-0 event; (b) the widely cited "Sep 23 Boeing criticism" is from **Sep 23 2023**, not 2026 — on **Sep 23 2026 8:19 PM ET** Trump instead praised Boeing for Türkiye/Bangladesh 111-plane orders (trumpstruth.org/statuses/41855; candidate to add as a second BA positive; also fix the incorrect "Sep 23 criticism" note on the Oct 1 BA entry); (c) **Bayer / BAYRY** Oct 3 ADDED 2026-10-17 03:00 UTC; (b) Sep 23 2026 BA praise ADDED and Oct 1 note fixed same run; (d) GM/F/STLA (Sep 26) ADDED 2026-10-17 03:15 UTC (1 Hern Ford sale overlap); Prysmian (Aug 31) ADDED 2026-10-17 03:20 UTC; Westinghouse already in exclusions.json (Oct 2025 $80B; CCJ proxy); MU/Micron already tracked (Jul 1); GOOGL Finland permitting criticism (Sep 14) ADDED 2026-10-17 ~03:50 UTC as **Company criticism** (first Negative #7 entry; 3 Quiver sales in window). Bombardier Sep 7 ADDED 2026-10-17 ~04:25 UTC as Company criticism (BBD-B.TO, CAD; no BDRBF Quiver trades; Gulfstream passing reference not scored). META Sep 6 post checked and REJECTED (about a Zuckerberg-funded nonprofit, ERIC/CEIR, not Meta the company). Remaining discovery leads (verify before adding): AAPL/MSFT/GOOGL 'Lake America' maps Sep 2–4; Aug 11 multi-company 'Radical Left SCAM' list (GOOGL/AAPL/V/GS/C/WFC/BAC/WMT/TM/TMUS — criticism of donors, not product); Anthropic private (exclude). Congress overlaps for LMT re-pulled 2026-10-17 (6 Hern sales). trumpstonks.com still ~1,415 mentions through Oct 16. Whenever new mentions are added, re-run the Quiver overlap parse.
12e. **Sector-ETF reaction per post** (idea from TipRanks Trump dashboard, which tags posts with sector ETF moves like XLC): show the matching SPDR sector ETF move next to each mention. DONE 2026-10-17 for single stocks (`sectors.json`, panel + lookup column). Industry-level peers DONE 2026-10-17 ~05:40 UTC (`peer` in sectors.json → SMH/URA/REMX/ITA/CARZ/IGV/IHE/IHI/SLX/FDN/KCE; `peer_ex` in data.json; panel tables + lookup column + glossary). Sector + peer fund overlay on the ticker-lookup chart DONE 2026-10-17 ~05:55 UTC (`tkpx.etf`, `sec`/`peer` per ticker, caption). Plain-English tappable chart key DONE 2026-10-17 ~06:00 UTC (`tkKey`, `#tkKey`). Next: per-post sector tags for sector/theme calls; mention the marker shapes in the lookup caption.
12f. **Same-post dedupe** (trumpstonks counts multiple excerpts from one post as one position): flag mentions sharing a source URL and count them once in averages. DONE 2026-10-17 (`post` id in update.py keyed on who+date+source, checkbox toggle). Grouping keyed on `orig_url` (falls back to source) DONE 2026-10-17 ~06:45 UTC (DJT+SPY Apr 9 2025 now p3). $1,000-per-post portfolio split DONE 2026-10-17 ~07:30 UTC (`port()` weights by `post` group when DEDUP; `#pUnit` heading; insights sentence). Next: split UCSB daily-archive sources by post timestamp.
12d. **Per-company pages / mention timeline chart** (trumpstockwatcher.com, whatdoes.live): chart with every mention marked. Mostly DONE via #10 (2026-10-17). All-mentions timeline DONE 2026-10-17 03:25 UTC (`cTL` scatter, horizon select, click-through). Monthly mention-count bars DONE 2026-10-17 03:45 UTC (`cTLm`, stacked by group, pre-2024 noted). Click a month bar to filter the all-mentions table DONE 2026-10-17 ~04:30 UTC (`TM`, `#tblM` banner, Show all months). Month highlight in the timeline (faded other months, caption line, shared Show all months) DONE 2026-10-17 ~04:45 UTC (`tlRe`, `TLA`, `#tlMx`). Policy-event lines DONE 2026-10-17 ~08:20 UTC (`PEV` list, `pevPlug` Chart.js plugin, `#tlEv` key with ±7-day counts; EO 14257 Apr 2 2025, EO 14266 Apr 9 2025, Geneva joint statement May 12 2025, Truth API Aug 1 2026). Next: more sourced events (e.g. Jul 9/Aug 1 2025 tariff deadlines, Section 232 actions) only after checking the official text; same lines on the ticker-lookup chart DONE 2026-10-17 ~08:30 UTC (`pevCat` category-axis plugin, `tkEv` key line); month filter for other panels.

12g. News-sourced Trump Truth Social times DONE 2026-10-17 ~06:40 UTC (KO Jul 16 2025 4:19 PM ET and INTC Apr 29 2026 6:20 PM ET found after close; NVDA/AEO/SPY before close; `archive_url` field + "post" link in Src column). Remaining untimed Trump rows are speeches/remarks (DELL ×3, TSLA, magnets, oil/coal/nuclear baskets) — times would come from Roll Call Factba.se / WH video, not post IDs; BTC/ETH Mar 2 2025 (crypto, Sunday, no entry effect). Archive-sourced Truth Social times DONE 2026-10-17 ~06:30 UTC (`orig_url` on 5 trumpstruth.org-sourced rows; INTC Aug 22 2025 5:04 PM ET → after-close, entry Aug 25). Next: UCSB/news-sourced Trump mentions (find each post on trumpstruth.org and add `orig_url`), and the X-sourced family crypto posts. 12g. Post-ID timestamps DONE 2026-10-17 ~06:20 UTC (`_post_time()` in update.py decodes Truth Social ids >>16 and X snowflakes; `time_et`/`time_src` on 28 rows; auto `after_close` for weekday >=16:00 ET; found PSQH Feb 4 2026 5:18 PM ET). Next: times for mentions sourced to trumpstruth.org/UCSB/news (read the archive's Original URL status ID and decode it), and Don Jr/Eric X crypto posts dated by UTC day. 12g. DONE 2026-10-17 ~06:10 UTC for the 4 after-close mentions with known times (`after_close` in mentions.json, `windows(..., after_close)`, 'counted from' flag). Next: backfill post times for older Trump mentions from trumpstruth.org/UCSB so more after-close posts get caught; store `time_et`. 12g. **Post-timing aware entry price** (pre-market vs after-close posts, e.g. BDX posted 11:18 PM ET): use the first tradable close after the post as day 0 when the post is after 4 PM ET. Needs post timestamps in mentions.json (overlaps #5).
12h. **Archive cross-check source** (also supertrumptracker.com/day/YYYY-MM-DD daily post lists and truthbell.app per-post ticker/sentiment tags, found 2026-10-17; use only as discovery leads, verify against the original post): trumpstruth.org and the UCSB American Presidency Project publish daily Truth Social archives with original URLs and timestamps; use them for mention discovery and timestamping.

12i. (Spin-off lead VERIFIED and ADDED 2026-10-17 ~04:50 UTC: decision was in the Jun 10 2026 8-K, not Oct; StreetInsider headline was a re-report. Next: watch for the S-4 going effective / shareholder vote date and add as milestones.) **Family-company stock context** (news 2026-10-16: DJT closed at a record low of $6.99, per WSJ/Yahoo; TAE merger S-4 pending). DONE 2026-10-17 for DJT/PSQH/ABTC (`family_cos.json`, panel + chart + insights). Next: add TZUP/ALTS if Yahoo prices return; optional Rumble (RUM) only if a family equity stake is documented in an SEC filing (GC role alone is not enough).

12j. **Truth API early-access context** DONE 2026-10-17 03:40 UTC (panel `#apiPanel`, glossary; before/after Aug 1 split by date using truthsocial/trumpstruth source URLs — note many earlier Trump mentions cite WH/UCSB URLs, so the 'before' set is small; next: tag every Trump mention with its original platform field, and add the SDNY ruling when it comes). Original note: (Business Insider, Oct 2026: Trump Media sells early access to Trump's posts for up to $100K/month since Aug 2026; it has been sued over it). Add a neutral explainer card and, if post timestamps are stored (#5/#12g), flag mentions posted after the API launch. Sourced context only.

## P2: UX & ops
13. RSS/JSON feed of new mentions, plus email/Telegram alerts (requires user approval for any sending). RSS + JSON Feed DONE 2026-10-17 ~06:45 UTC (`feed.xml`, `feed.json` from update.py; header links + `<link rel=alternate>`; in publish.sh allow-list and watchlist guard). Per-group feeds DONE 2026-10-17 ~07:40 UTC (`_write_feed()`; feed-trump/family/admin .xml/.json; header links; publish allow-list + guard on feed*). Next: per-ticker feeds; alerts still need the user's approval.
14. Mobile layout pass, and accessible colour palette (colour-blind safe). Section navigation DONE 2026-10-17 ~04:00 UTC (header "Jump to" links, sticky jump menu, back-to-top, sticky-offset `goSec()`). Collapsible filter bar DONE 2026-10-17 ~04:05 UTC (`#fTog`, `#fSum` summary, collapsed by default ≤760px; jump menu in top row). Next: colour-blind check of the Trump/Family/Admin palette (amber/violet/cyan is already fairly CVD-safe; verify with a simulator and add shape/pattern cues in charts), Sticky first column + swipe hint on wide tables (≤760px) DONE 2026-10-17 ~04:10 UTC. Asset column pinned in the all-mentions table (≤760px, `.tblw`) DONE 2026-10-17 ~04:15 UTC. Colour-blind shape cues DONE 2026-10-17 ~04:20 UTC (`GS`/`GSY`: ● Trump, ▲ Family, ◆ Admin in cTL, tkC markers, group tags; CVD sim: Family–Admin ΔE≈25 deutan). Pinned-cell row highlight DONE 2026-10-17 ~06:15 UTC (`tr.hl>td` rule in the ≤760px block). Pattern fills DONE 2026-10-17 ~09:05 UTC (`pat()` canvas patterns: solid Trump, stripes Family, dots Admin on cEach + cTLm; legend labels with GSY). Next: same fills for any other group-coloured bars (e.g. stance panel) if added. Newest mentions panel DONE 2026-10-17 ~09:15 UTC (`newest(sel)`, `#secNew`, 6 latest in filters with plain result vs index; Jump-to entry). Next: a "new since your last visit" highlight using localStorage.
15. Scheduled daily refresh via GitHub Actions running update.py (needs yfinance in CI; keep `private/` excluded).
16. Automated tests: JS error check (playwright), data schema validation, "no private content in public files" guard in CI. DONE locally 2026-10-17 ~10:20 UTC: `check.py` (JSON/XML parse, mentions schema, private-text markers from private/watchlist.json, page/console errors + chart count at 1280/390px, `--live`), run by publish.sh before push. Next: run it in GitHub Actions (needs playwright install; private markers unavailable there, so CI would only do the generic checks).
17. Shrink index.html. PROGRESS 2026-10-17 ~07:35 UTC: 7-significant-digit floats + compact embed (`_compact` in update.py) took index.html 1.16 MB → 0.97 MB (gzip 384 → 319 KB) with identical rendered text (5 digits changed some displayed values, so don't go lower). Next: drop unused benchmark keys from per-row `ex`, or load data.json lazily.

## Known data gaps / caveats to revisit
- Private companies (Goya, Trump Org deals), delisted/no-data tokens: see exclusions.json.
- Crypto and futures have no congressional/OGE ticker coverage.
- Family memecoin launch-day prices are thin and volatile, which skews day-0 averages (median shown alongside).
- 2026-10-17 news check: DJT closed at a record low $6.99 on Oct 16 (Yahoo/WSJ/MarketBeat), tied to high-beta selling and the pending TAE merger; rebounded briefly Oct 15 then fell again; no new verified *company promotion* mentions found for Oct 15–17 in this sweep (DJT price news only). #12i panel shipped. Scout also noted trumpstonks.com still listing ~1,415 mentions through Oct 16.
- Two private watchlist rows were verified on 2026-10-17 (ACDC/Reuters; CFTC Perez order). Re-verify the other rows periodically.

## Research framing goal (README, 2026-10-17)
The public README frames the project as an open experiment. It tests whether public data shows patterns *consistent with* the concerns of the STOCK Act, the Ethics in Government Act/OGE rules (5 CFR 2634/2635), 18 USC 208, SEC Rule 10b-5, and CEA §6(c)(1)/CFTC Rule 180.1 (incl. the Feb 2026 event-contract advisory). Next steps toward that goal:
1. **Peer-outperformance ranking (P0).** Reconstruct trade-level returns for every disclosing Member of Congress and senior official with 278-Ts (amount-range midpoints) and linked funds (13F/13D). Compare vs peers (chamber/party/committee; fund style) and benchmarks using alpha, information ratio and hit rate at +30/+90/+180d. Use placebo-date and multiple-comparison controls. Publish as statistical outliers with caveats, never accusations. **Congress part DONE 2026-10-17** (Rankings tab, `rank.py` → `rankings.json`): 64 current members ranked (≥10 scored trades on ≥8 dates since 2023, 34,587 Quiver/House Clerk/Senate eFD trades), sign×(stock−SPY) at +30/+90d, date-clustered bootstrap 95% range, hit rate, $-weighted (range midpoints), vs chamber mean, BH q-values. Price cache `../congress/pxcache.pkl` (local, includes `_bad` set of unpriceable tickers); refresh member data with `../congress/qmem.py`/`qraw.py`, then `python rank.py` (Yahoo rate-limits bursts: wait and rerun). STILL OPEN: officials/family entities (OGE 278-T PDFs have no machine-readable dated trade list), former members, options/funds, sector-adjusted benchmark, rerun rank.py weekly.
2. **Random-date baselines (P0).** PROGRESS 2026-10-17 ~05:10 UTC: placebo-date baseline for day-0 and +30d returns vs S&P 500 DONE (`plc` per row, `#secPlc`, `plcPanel`). Pre-comment moves baseline DONE 2026-10-17 ~05:35 UTC (`plc.pre`, `preBase()`, `#preB`; 13 of 64 in asset's top-10% pre-moves vs 6.4 expected). Next: the same random-date baseline for congressional-trade overlap counts (needs full per-ticker trade history from Quiver/House Clerk) and for the pre-mention moves panel. For congressional and disclosure overlaps and pre-moves, compute the overlap rate expected on random non-mention dates for the same tickers, so the dashboard can say whether counts exceed chance.
3. **Beta/factor-adjusted abnormal returns + clustered SEs (P1).** Also report significance on the dashboard in plain English.
4. **Committee-relevance tagging (P1).** DONE 2026-10-17 ~06:55 UTC (`committees.json`: current seats from unitedstates/congress-legislators + our ticker→committee guide; `cmte`/`cmte_chk` per trade; table column + `cmNote`; 19 of 78 rows match). Next: seats on the trade date (historical membership via congress.gov), subcommittee-level matching, and a random-member baseline for how often a related-committee match happens by chance. Flag congressional trades where the member sits on a committee with jurisdiction over the sector (public committee rosters).
5. **Filing-lag tracking (P1).** DONE 2026-10-17 using Quiver's listed filing dates (`filed` in congress.json, days-to-file column, >45d flag, public-before-comment count). House cases DONE 2026-10-17 ~05:15 UTC (McClain KO Filing #20030891 and Rulli AAPL #20035147: both original reports, not amendments; `ptr` field + table links). Senate cases DONE 2026-10-17 ~05:25 UTC (Britt NVDA PTR filed Jan 26 2026, 22 spouse trades; Armstrong PLTR PTR filed Jul 21 2026, 703 trades, same day as his New Filer Report dated Mar 24 2026; both originals, no amendments). Next: auto-flag any new >45d trade for checking; also House Clerk annual index `public_disc/financial-pdfs/<year>FD.zip` lists every PTR DocID for cross-checking Quiver completeness (#1).
6. **Keep the language neutral.** Every README/dashboard update must avoid naming or implying that any individual broke a law.
- **2026-10-17 scout (trumpstonks):** Oct 14 also named a Korea $50B infrastructure deal and a Taiwan offtake commitment for Alaska LNG (no single listed ticker — track as sector/theme or exclusion).

## Scout notes (2026-10-17 ~03:20 UTC)
- **Peers:** trumptrack.app still leads on OGE 278-T volume (~3.6K Q1 2026) and now surfaces a Predictions page (Claude-calibrated P(up)); it also monitors signed bills via congress.gov — backlog idea if not already covered: ingest WH/bill signing company mentions as a separate source class. trump-meter.com overlays Fed/geopolitical/energy sentiment on indexes (broader than company mentions). whitehouseticker.com classifies WH events and post-mention windows (similar to our horizons). trumpsnp.com is an interactive Trump-post → S&P chart (overlaps our portfolio/index matrix). trumpstonks.com still ~1,415 mentions through Oct 16; no new finishable listed-ticker candidates beyond Prysmian this sweep.
- **News:** No new verified company-promotion mentions for Oct 15–17 beyond prior DJT price coverage. Westinghouse remains private (exclusions + CCJ proxy); Saudi civil-nuclear Truth Social posts did not name Westinghouse as a ticker.
- **This run:** Verified and added Prysmian Aug 31 from primary Truth Social + trumpstruth.org; Quiver re-checked (empty window).

## Scout notes (2026-10-17 ~03:25 UTC)
- **News:** Public Citizen report (Oct 16) says 205 companies whose federal enforcement actions were dropped gave $210.5M to pro-Trump PACs. Possible future *context* card (sourced, neutral) if it intersects tracked tickers; verify the primary report first. No new verified company-promotion mentions Oct 15–17.

## Scout notes (2026-10-17 ~03:30 UTC)
- **News:** Oct 16 coverage is still DJT's record-low close ($6.99; Innercircle Ledger / MarketBeat / 24/7 Wall St., which also notes Rumble fell 8% the same day). No new verified company-promotion mentions Oct 16–17.

## Scout notes (2026-10-17 ~03:40 UTC)
- **News:** Truth API litigation: D.D.C. complaint (American Oversight & CfA, Sep 17), SF City Attorney suit (Sep 23, Cal. UCL), SDNY The Intercept Media v. Trump 1:26-cv-6867 PI hearing Oct 7 (Oetken reserved decision). Watch for the ruling. No new verified company-promotion mentions Oct 16–17.

## Scout notes (2026-10-17 ~03:45 UTC)
- **News:** No new verified company-promotion mentions Oct 16–17. Stories: Public Citizen PAC report (already noted), resurfaced Sep 28 2025 CBD video Trump shared (no ticker named; not a company mention), Strive (ASST) $630M preferred raise (no Trump mention), Palantir −6% Oct 16 and Micron swings (both already tracked tickers; price news only).

## Scout notes (2026-10-17 ~03:50 UTC)
- **Peers:** trumpstonks.com still ~1,415 mentions through Oct 16; Sep 14 GOOGL Finland criticism verified from primary Truth Social + trumpstruth.org/statuses/41720 + Yle/Reuters and added this run. trumptrack.app still leads OGE 278-T volume (~3.6K Q1 2026) and Predictions; TipRanks tags Trumpy/Grumpy/Neutral (overlaps #7). No new finishable peer UX beyond month-bar click (#12d) and industry ETFs (#12e).
- **News Oct 15–17:** No new verified *company-promotion* mentions. Coverage: GlobalFoundries stakeholder reaction (already tracked Oct 14), DJT record-low close $6.99 Oct 16 (WSJ / 24/7 Wall St.; #12i already shipped), Rumble −8% same day (no documented family equity stake → keep out of family_cos).
- **New backlog ideas:** (1) verify trumpstonks discovery leads listed under #12c (META Sep 7; Bombardier; Lake America maps; Aug 11 donor-list criticism — decide per-ticker inclusion rules for donor lists). (2) TipRanks-style stance labels on every mention once #7 has ≥5 rows. (3) WH mobile-app alerts as an additional source class (whitehouse.gov Mar 2026 app) — discovery only.
- **This run:** Added GOOGL Company criticism + 3 Quiver overlaps.

## Scout notes (2026-10-17 ~03:55 UTC)
- **News:** Oct 16 coverage still DJT record-low close ($6.99; 24/7 Wall St., Innercircle Ledger, MarketBeat) and Rumble −8%. No new verified company-promotion mentions Oct 16–17.
- **This run:** BH adjustment on the per-group luck grid.

## Scout notes (2026-10-17 ~04:00 UTC)
- **News:** Oct 16 coverage still DJT record-low close ($6.99; Yahoo, 24/7 Wall St., Innercircle Ledger, MarketBeat) and Rumble −8%. No new verified company-promotion mentions Oct 16–17.
- **This run:** Section navigation (UX #14).

## Scout notes (2026-10-17 ~04:05 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; Yahoo, MarketBeat, Revenue Spotlights citing Sept CPI 3.7% and Truth Social traffic). No new verified company-promotion mentions.
- **This run:** Collapsible filter bar (UX #14).

## Scout notes (2026-10-17 ~04:10 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; WSJ, Revenue Spotlights, StockAnalysis). No new verified company-promotion mentions.
- **This run:** Sticky first column on wide tables for phones (UX #14).

## Scout notes (2026-10-17 ~04:15 UTC)
- **News:** No new verified company-promotion mentions Oct 16–17. Stories: Public Citizen PAC report, Strive (ASST) $630M preferred, ABC corrected story on 1789 Capital's $50M Anduril stake (Anduril private; possible neutral family-investment context note only if sourced to primary filings).
- **This run:** Pinned Asset column in all-mentions table on phones (UX #14).

## Scout notes (2026-10-17 ~04:20 UTC)
- **News:** No new verified company-promotion mentions Oct 16–17. Stories: resurfaced Sep 28 2025 CBD video (no ticker), Public Citizen PAC report, Strive $630M preferred, Palantir −6% (tracked; price news), Moderna +700% YTD (no Trump mention found), Treasurer Beach Trump $1 coin.
- **This run:** Colour-blind shape cues (UX #14).

## Scout notes (2026-10-17 ~04:25 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; Yahoo, MarketBeat, Revenue Spotlights). No new verified company-promotion mentions.
- **This run:** Added Bombardier Sep 7 Company criticism (#7/#12c); rejected META lead. Next criticism leads: Aug 11/Sep 7 donor-list post (needs an inclusion rule for donor lists), Lake America maps Sep 2–4. Idea: a small 'Criticism vs praise' comparison once #7 has 5+ rows.

## Scout notes (2026-10-17 ~04:30 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; Yahoo, StockAnalysis, Revenue Spotlights). No new verified company-promotion mentions.
- **This run:** Month-bar click filters the all-mentions table (#12d).

## Scout notes (2026-10-17 ~04:35 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; Yahoo, StockAnalysis, MarketBeat, 24/7 Wall St. with Rumble −8%). No new verified company-promotion mentions.
- **This run:** BH adjustment on the industry (sector) panel (#8).

## Scout notes (2026-10-17 ~04:45 UTC)
- **News:** Oct 16 coverage still DJT 52-week/record low (~$6.93–6.99; MarketBeat, 24/7 Wall St., Invezz). New lead: StreetInsider says Trump Media abandoned the Truth Social spin-off to focus on the TAE merger (verify primary filing). No new verified company-promotion mentions.
- **This run:** Month highlight carried into the timeline (#12d).

## Scout notes (2026-10-17 ~04:50 UTC)
- **News/filings:** EDGAR shows DJT's latest filings are an Oct 2 S-4 delaying amendment (DEL AM) and Oct 1 425 merger communications; no new 8-K since Sep 30. No new verified company-promotion mentions Oct 16–17.
- **This run:** Jun 10 2026 Truth Social spin-off drop added as a DJT milestone (#12i).

## Scout notes (2026-10-17 ~04:55 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; WSJ, Yahoo, 24/7 Wall St., Margin Beacon citing SimilarWeb Truth Social traffic). No new verified company-promotion mentions.
- **This run:** Per-category luck grid with BH adjustment (#8).

## Scout notes (2026-10-17 ~05:00 UTC)
- **News:** Oct 16–17 coverage unchanged (resurfaced 2025 CBD video, Public Citizen PAC report, Strive $630M preferred, Palantir −6%, Moderna +700% YTD, Trump $1 coin). No new verified company-promotion mentions.
- **This run:** By-sector luck checks with BH adjustment (#8).

## Scout notes (2026-10-17 ~05:05 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; WSJ, StockAnalysis, Margin Beacon citing SimilarWeb Truth Social traffic of 15.31M visits in Sep). No new verified company-promotion mentions.
- **This run:** Beta-adjusted returns panel (#9 / research #3).

## Scout notes (2026-10-17 ~05:10 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.94–6.99; 24/7 Wall St., WSJ, Margin Beacon) and Business Insider on Truth API early access. No new verified company-promotion mentions.
- **This run:** Random-date (placebo) baseline panel (research #2).

## Scout notes (2026-10-17 ~05:15 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; WSJ, StockAnalysis, Margin Beacon) and Washington Post (Oct 15) on Truth Social traffic falling to about 260K daily users in Sep. No new verified company-promotion mentions.
- **This run:** House late-filing cases checked against official House Clerk PTRs (research #5).

## Scout notes (2026-10-17 ~05:25 UTC)
- **News:** Oct 16–17 coverage still DJT record low (WSJ Oct 16 'Trump Media Stock Has Never Been Worth Less'; Margin Beacon Oct 17, ~$6.90). No new verified company-promotion mentions.
- **New lead for #6 (OGE 278-T):** CNN investigation (Jul 16 2026, cnn.com/2026/07/16/us/trump-stock-sales-truth-social-invs-vis) reports at least 44 purchases of 21 companies within a week before favorable Truth Social posts, and 17 purchases of 8 companies before negative posts, from Trump's OGE 278-T filings (White House says trades are managed independently). Idea: a 'Did Trump's own disclosed trades precede the post?' column using the primary 278-T PDFs (verify each trade against OGE, not CNN). Neutral framing only.
- **This run:** Senate late-filing cases checked against Senate eFD (research #5).

## Scout notes (2026-10-17 ~05:35 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.90–6.99; 24/7 Wall St., Margin Beacon, Invezz, WSJ). A Trump Truth Social post on the market's record high and falling oil named no company. No new verified company-promotion mentions.
- **This run:** Random-date baseline for pre-comment moves (research #2).

## Scout notes (2026-10-17 ~05:40 UTC)
- **Peers:** trumpstonks.com still ~1,415 mentions through Oct 16. TipRanks Trump dashboard still tags posts with sector ETF moves (XLC etc.) — industry peers (SMH/URA/REMX/…) shipped this run. trumptrack.app still leads OGE 278-T volume (~3.6K Q1 2026) and Predictions. Kalshi/Polymarket October “what companies will Trump say” markets (SpaceX, Paramount, Toyota, etc.) noted as optional aggregate context for #12.
- **News Oct 16–17:** No new verified company-promotion mentions. Coverage still DJT's record-low close (~$6.90–6.99; WSJ, Margin Beacon). Westinghouse Oct 1 nuclear posts remain in exclusions (private; CCJ proxy).
- **Discovery leads (not added):** Lake America map posts Sep 2 (AAPL/GOOGL) and Sep 4 (Google/Apple/Microsoft Maps) are verified on trumpstruth.org but are policy/rename affirmations, not investment praise — keep as optional Policy promotion only if inclusion rules expand. Aug 11 donor-list criticism still needs an inclusion rule. Alabama-rally names (Peterbilt, Mercedes, U.S. Steel, Eli Lilly, ArcelorMittal) need primary-source verification before adding.
- **This run:** Industry peer ETFs (#12e).

## Scout notes (2026-10-17 ~05:55 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; Yahoo, MarketBeat 52-week low $6.93, Margin Beacon Oct 17). No new verified company-promotion mentions.
- **This run:** Sector/industry fund lines on the ticker-lookup chart (#12e).

## Scout notes (2026-10-17 ~06:00 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; exa/StockAnalysis, WSJ, Margin Beacon Oct 17, CoinDesk on Truth Social daily users down to ~260K). No new verified company-promotion mentions.
- **This run:** Plain-English tappable key on the ticker-lookup chart (#12e).

## Scout notes (2026-10-17 ~06:10 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.94–6.99; 24/7 Wall St., Margin Beacon, WSJ). TipRanks dashboard shows an Oct 16 8:28 PM ET Truth Social post backing Paxton over Cornyn that criticised Fox News (FOXA +0.27%, XLC −1.89% tags). Lead only: needs an inclusion rule for political criticism of media companies before adding. No new verified company-promotion mentions.
- **This run:** After-close posts now enter on the next trading day (#12g).

## Scout notes (2026-10-17 ~06:15 UTC)
- **News:** Trump's Oct 17 12:11 AM ET Truth Social post "Best in History!" (trumpstruth.org/statuses/42396) is an S&P 500 30%-gain graphic, no company named; not a mention. DJT coverage still record low (~$6.90–6.99; Margin Beacon Oct 17, WSJ Oct 16). No new verified company-promotion mentions.
- **This run:** Row highlight kept on the pinned column on phones (UX #14).

## Scout notes (2026-10-17 ~06:20 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.94–6.99; 24/7 Wall St. and Invezz Oct 16, Margin Beacon Oct 17, WSJ). Trump's Oct 17 "Best in History!" post names no company. No new verified company-promotion mentions.
- **This run:** Exact post times decoded from Truth Social / X post IDs; PSQH Feb 4 2026 moved to after-close (#12g).

## Scout notes (2026-10-17 ~06:30 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.90–6.99; 24/7 Wall St., Invezz, Margin Beacon) and Reuters on Friday's AI-led selloff (S&P 500 −1.2%). Trump's Oct 17 "Best in History!" post names no company. No new verified company-promotion mentions.
- **This run:** Post times for the 5 trumpstruth.org-sourced mentions; Intel Aug 22 2025 found to be after close (#12g).

## Scout notes (2026-10-17 ~06:40 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.90–6.99; 24/7 Wall St. with Rumble −8%, Margin Beacon Oct 17, WSJ Oct 16). Trump's Oct 17 "Best in History!" post names no company. No new verified company-promotion mentions.
- **This run:** Exact post times for 5 news-sourced Trump mentions; KO and INTC found to be after close (#12g). Idea: same-post grouping should also key on `orig_url` (DJT and SPY Apr 9 2025 are one post but are not tagged "same post" because their sources differ).

## Scout notes (2026-10-17 ~06:45 UTC)
- **News:** Oct 16–17 coverage unchanged (resurfaced Sep 2025 CBD video, Public Citizen PAC report, Strive $630M preferred, Palantir −6%, Moderna +700% YTD, Trump $1 coin, SoFi). No new verified company-promotion mentions.
- **This run:** Same-post grouping keyed on the original post link (#12f); DJT and SPY Apr 9 2025 now grouped.

## Scout notes (2026-10-17 ~06:50 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.90–6.99; WSJ Oct 16, 24/7 Wall St. with Rumble −8%, Margin Beacon Oct 17). Trump's Oct 17 "Best in History!" post names no company. No new verified company-promotion mentions.
- **This run:** RSS + JSON feeds of mentions (#13).

## Scout notes (2026-10-17 ~06:55 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; Yahoo, MarketBeat 52-week low $6.93, 24/7 Wall St. with Rumble −8%). No new verified company-promotion mentions.
- **This run:** Related-committee column for congressional trades (research #4).

## Scout notes (2026-10-17 ~07:00 UTC)
- **News:** Oct 16–17 coverage still DJT record-low close ($6.99; exa/StockAnalysis, Margin Beacon and Invezz on Truth Social traffic and losses, WSJ Oct 16). No new verified company-promotion mentions.
- **This run:** Plain-English 'Members of Congress' insights bullet (counts, buys, public-before-comment, related committee). Next insights ideas: a bullet for the ordinary-days baseline and the beta-adjusted read if not already summarised; per-group feeds (#13).

## Scout notes (2026-10-17 ~07:05 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.90–6.99; Margin Beacon Oct 17). Oct 8 coverage of Trump's August OGE 278-T (517 trades; CNBC, Yahoo/Moneywise, Reuters) had not been folded in. No new verified company-promotion mentions.
- **This run:** Added Aug 21 2026 DELL and BA sales (#6). Remaining August-278-T leads for tracked tickers: NVDA (bought up to ~$1.6M incl. $500,001–$1M Aug 17, sold $500,001–$1M Aug 21, per Reuters/Yahoo) is far from the only NVDA mention (Apr 2025), so not shown; check the primary OGE PDF for INTC/MP/TSLA/AAPL/GOOGL/LMT/GM/F trades in Aug 2026 near tracked mentions. Idea: plain-English insights line on Trump's own disclosed trades vs his mentions — **DONE 2026-10-17 ~07:10 UTC** (insights bullet; 14 mentions, 11 purchase-before / 3 sale-after / 2 sale-before / 1 same-day).

## Scout notes (2026-10-17 ~07:10 UTC)
- **Peers / news:** No new verified company-promotion mentions Oct 16–17. Coverage still DJT record low (~$6.90–6.99; Margin Beacon Oct 17, WSJ Oct 16) and the resurfaced Sep 28 2025 CBD video (no ticker). Peer trackers unchanged this sweep (trumptrack.app OGE volume; trumpstonks.com ~1,415 through Oct 16; TipRanks stance/sector tags; Capitol Trades / Quiver for Congress). FOXA Oct 16 media-criticism lead and Lake America / Aug 11 donor-list leads still need inclusion rules — not added.
- **Aug 278-T follow-up:** CNBC/Yahoo/Reuters Oct 8 coverage re-checked for tracked tickers near mention windows. DELL and BA sales already in disclosures.json. NVDA Aug buys/sale remain far from the Apr 2025 mention (not shown). INTC Aug 2026 sale ($100k–$250k per secondary summaries) is far from the Aug 2025 / Apr 2026 Intel mentions; no verified Aug 2026 AAPL/GOOGL/LMT/GM/F/TSLA/MP trades falling near our tracked windows in those stories. Primary OGE PDF still worth a later pass for completeness (#6).
- **This run:** Plain-English "Trump's own disclosed trades" insights bullet (purchase-before / sale-after / opposite / same-day counts from disclosures.json). Next insights ideas: none urgent; optional UX #12e marker-shapes in lookup caption, #14 pattern fills, #12f $1,000-per-post portfolio.

## Scout notes (2026-10-17 ~07:25 UTC)
- **News:** Oct 16–17 coverage still DJT record low (~$6.90–6.99; Margin Beacon Oct 17, WSJ Oct 16) and Trump's Oct 17 "Best in History!" S&P 500 graphic (no company named). No new verified company-promotion mentions.
- **This run:** Merged the beta insights bullet into one fuller "Adjusting for jumpiness" line (comment day + held to date + which windows survive the BH correction + link). Ordinary-days baseline bullet already existed. Next insights ideas: per-group feeds (#13), $1,000-per-post portfolio split (#12f), primary OGE Aug 2026 PDF pass (#6).

## Scout notes (2026-10-17 ~07:30 UTC)
- **News:** Oct 16–17 coverage still DJT's $6.99 record-low close (MarketBeat 52-week low $6.93, 24/7 Wall St. with Rumble −8%, Yahoo). No new verified company-promotion mentions.
- **This run:** $1,000-per-post portfolio split when "Count each post once" is ticked (#12f). Next ideas: per-group feeds (#13), primary OGE Aug 2026 PDF pass (#6), shape cues on cEach bars (#14).

## Scout notes (2026-10-17 ~07:35 UTC)
- **News:** Oct 16–17 coverage still DJT's $6.99 record-low close (WSJ, StockAnalysis, EODData; no Oct 17 session). No new verified company-promotion mentions.
- **This run:** Smaller page via 7-significant-digit floats and compact embed (#17). Next ideas: per-group feeds (#13), primary OGE Aug 2026 PDF pass (#6), shape cues on cEach bars (#14).

## Scout notes (2026-10-17 ~07:40 UTC)
- **News:** Oct 16–17 coverage still DJT's $6.99 record-low close (WSJ, StockAnalysis, EODData; no Oct 17 session). No new verified company-promotion mentions.
- **This run:** Per-group RSS/JSON feeds (#13). Next ideas: primary OGE Aug 2026 PDF pass (#6), shape cues on cEach bars (#14), marker shapes in lookup caption (#12e).

## Scout notes (2026-10-17 ~07:45 UTC)
- **News:** X news sweep (24h): resurfaced Sep 28 2025 CBD video, Trump Paxton/Cornyn Texas Senate posts, Strive $630M preferred, Palantir −6% Oct 16, Treasurer's Trump $1 coin video. No new verified company-promotion mentions.
- **This run:** Plain-English caption + group shapes + tap-to-lookup on the "Each mention" bar chart (`eachCap`, `#eachN`; #14 shape cues on cEach DONE). Marker shapes in the lookup key already shown via `tkKey` (#12e item effectively DONE). Next ideas: primary OGE Aug 2026 PDF pass (#6), policy-event annotations on the timeline (#12d), plain-English captions for the cEx and portfolio charts if missing.

## Scout notes (2026-10-17 ~07:50 UTC)
- **News:** X news sweep: resurfaced Sep 2025 CBD video, Public Citizen PAC report, Strive $630M preferred, Dell $6.25B children's accounts (no new Trump company mention found), SpaceX −4% Oct 13. No new verified company-promotion mentions.
- **This run:** Plain-English captions under the cEx (`exCap`, `#exN`) and portfolio (`eqCap`, `#eqN`) charts. Next ideas: primary OGE Aug 2026 PDF pass (#6), policy-event annotations on the timeline (#12d), captions for the index matrix and Trump vs Family vs Admin table if missing, stance-aware long/short (#12b, only 2 criticism entries so far).

## Scout notes (2026-10-17 ~07:55 UTC)
- **News:** X news sweep: resurfaced Sep 2025 CBD video, Public Citizen canceled-probes PAC report, Strive $630M preferred, ABC's corrected Trump sons/Anduril story (Oct 10; 1789 Capital, private, no listed ticker). No new verified company-promotion mentions.
- **This run:** Plain-English captions under the index matrix (`mxCap`, `#mxN`) and the Trump vs Family vs Admin table (`grpCap`, `#grpN`; table wrapped for sideways scroll). Next ideas: primary OGE Aug 2026 PDF pass (#6), policy-event annotations on the timeline (#12d), stance-aware long/short (#12b), captions for the sector/industry and disclosure panels if missing.

## Scout notes (2026-10-17 ~08:05 UTC)
- **News:** X news sweep: resurfaced Sep 2025 CBD video, Public Citizen canceled-probes PAC report, Treasurer's Trump $1 coin video, AP-NORC poll on Trump's business focus, Dell children's accounts. No new verified company-promotion mentions.
- **This run:** Plain-English caption at the top of the disclosure overlap panel (`discCap`, `#discCap`; table wrapped for sideways scroll). Next ideas: caption for the Congressional trades panel and the sector/industry panel if missing, primary OGE Aug 2026 PDF pass (#6), policy-event annotations on the timeline (#12d), stance-aware long/short (#12b).

## Scout notes (2026-10-17 ~08:10 UTC)
- **News:** X news sweep (24h): resurfaced Sep 2025 CBD video, Public Citizen canceled-probes PAC report, Strive $630M preferred, Palantir −6% Oct 16, Treasurer's Trump $1 coin video, Moderna/SoFi/Zeta moves with no Trump comment. No new verified company-promotion mentions.
- **This run:** Plain-English caption at the top of the sector / theme calls panel (`sectCap`, `#sectCap`). Congress panel already has plain-English summaries (count, lag, committees). Next ideas: caption for the pre-comment moves panel if thin, primary OGE Aug 2026 PDF pass (#6), policy-event annotations on the timeline (#12d), stance-aware long/short (#12b).

## Scout notes (2026-10-17 ~08:20 UTC)
- **News:** X news sweep (24h): resurfaced Sep 2025 CBD video, Public Citizen canceled-probes PAC report, Strive $630M preferred, Palantir −6% Oct 16, Treasurer's Trump $1 coin, Moderna/SoFi/Zeta/TAO moves with no Trump comment. No new verified company-promotion mentions.
- **This run:** Numbered policy-event lines and a sourced plain-English key on the all-mentions timeline (#12d).

## Scout notes (2026-10-17 ~08:25 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Public Citizen PAC report, Trump $1 coin, Nebius −12%/GameStop 52-week high, MSCI to drop Strategy (MSTR) from global indexes Nov 30. None tied to a Trump/family/admin comment. No new verified company-promotion mentions.
- **This run:** Plain-English caption at the top of the pre-comment moves panel (`preCap`, `#preCap`; top run-ups/slides + what came next by group). Next ideas: primary OGE Aug 2026 PDF pass (#6), stance-aware long/short (#12b), S-4 effectiveness / TAE vote milestone watch (#12i), historical committee seats on trade date (#4).

## Scout notes (2026-10-17 ~08:30 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Public Citizen PAC report, Trump $1 coin, SOXX record nine-day losing streak, Nebius −12%, MSCI to drop Strategy. None tied to a Trump/family/admin comment. No new verified company-promotion mentions.
- **This run:** Policy-event lines + sourced key on the ticker-lookup chart (#12d). Next ideas: primary OGE Aug 2026 PDF pass (#6), stance-aware long/short (#12b), S-4 effectiveness / TAE vote milestone watch (#12i), more sourced policy events (Jul 9 / Aug 1 2025 tariff deadlines) after checking official text.

## Scout notes (2026-10-17 ~08:40 UTC)
- **News:** X news sweep: Trump $1 coin, Public Citizen PAC report, ABC's corrected Anduril story, Dell children's accounts, Oracle/GameStop moves. No new verified company-promotion mentions.
- **This run:** Added EO 14316 (Jul 7 2025, pause extended to Aug 1) and EO 14326 (Jul 31 2025, new country rates) to `PEV`, verified on federalregister.gov; `pevOff()` spaces close labels. Next ideas: Aug 11 2025 China pause extension and Sep 5 2025 EO 14346 only after checking text; stance-aware long/short (#12b); primary OGE Aug 2026 PDF pass (#6); TAE S-4 vote milestone watch (#12i).

## Scout notes (2026-10-17 ~08:45 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Treasurer's Trump $1 coin, MSCI to drop Strategy (MSTR) Nov 30, GameStop 52-week high, Anthropic/Blackstone chip financing. None tied to a Trump/family/admin comment. No new verified company-promotion mentions.
- **This run:** Added EO 14334 (Aug 11 2025, China pause extended to Nov 10 2025) to `PEV`, verified on federalregister.gov. Sep 5 2025 EO 14346 (scope changes / agreement procedures) checked on the Federal Register list but not added (less of a single market moment). Next ideas: Nov 2025 US–China follow-up only after checking official text; stance-aware long/short (#12b); primary OGE Aug 2026 PDF pass (#6); TAE S-4 vote milestone watch (#12i).

## Scout notes (2026-10-17 ~08:50 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Treasurer's Trump $1 coin, $TRUMP memecoin trader story (no verified wallet data), Nebius −12% / AI-infrastructure debt worries, SOXX nine-day losing streak, Anthropic/Blackstone chip financing. None tied to a Trump/family/admin comment. No new verified company-promotion mentions.
- **This run:** Added EO 14358 (signed Nov 4 2025; China pause extended to Nov 10 2026) to `PEV`, verified on federalregister.gov (doc 2025-19826). New watch item: the China pause expires 12:01 a.m. EST Nov 10 2026 — check for an extension or new order around then and add it only from official text. Next ideas: stance-aware long/short (#12b); primary OGE Aug 2026 PDF pass (#6); TAE S-4 vote milestone watch (#12i).

## Scout notes (2026-10-17 ~09:00 UTC)
- **News:** X news sweep: resurfaced Sep 2025 CBD video, Public Citizen PAC report ($210.5M from companies with canceled probes), Dell $6.25B children's accounts, Trump Texas Senate posts, ABC's corrected Anduril story. None is a new company-promotion mention. No new verified mentions.
- **This run:** Praise vs criticism panel (#12b). Next ideas: primary OGE Aug 2026 PDF pass (#6); TAE S-4 vote milestone watch (#12i); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch.

## Scout notes (2026-10-17 ~09:05 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Treasurer's Trump $1 coin, $TRUMP memecoin trader story (unverified), Nebius/CoreWeave AI-debt selloff, GameStop 52-week high, House GOP anti-fraud pledge backlash. None tied to a Trump/family/admin company comment. No new verified mentions.
- **This run:** Colour-blind fill patterns on the monthly and each-mention bars (#14). Next ideas: primary OGE Aug 2026 PDF pass (#6); TAE S-4 vote milestone watch (#12i); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch.

## Scout notes (2026-10-17 ~09:15 UTC)
- **News:** X news sweep: Oct 14 Bullhead City rally mentioned copper with no company named (theme only), resurfaced 2025 CBD video, Public Citizen PAC report, Strive $630M preferred, ABC Anduril correction. No new verified company-promotion mentions. EDGAR (CIK 1849635): latest DJT filing still the Oct 2 S-4 delaying amendment; no effectiveness or vote date yet.
- **This run:** Newest mentions panel (readability). Next ideas: primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); "new since last visit" highlight; China tariff pause expiry Nov 10 2026 watch.

## Scout notes (2026-10-17 ~09:20 UTC)
- **News:** X news sweep (12h): resurfaced CBD video, Trump $1 coin, $TRUMP memecoin trader story (unverified), Nebius/CoreWeave AI-debt selloff, GameStop 52-week high, Moderna insider sale. None tied to a Trump/family/admin company comment. No new verified mentions.
- **This run:** "New since your last visit" marks in the Newest mentions panel (`SEEN`, `NK()`, localStorage key `tmt_seen_v1` with cur/prev snapshots so reloads keep marks). Next ideas: also tag new rows in the all-mentions table; primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone watch (#12i).

## Scout notes (2026-10-17 ~09:25 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Treasurer's Trump $1 coin, $TRUMP memecoin trader story (unverified), Nebius −25% week, GameStop 52-week high, Moderna insider sale, MSCI dropping Strategy. None tied to a Trump/family/admin company comment. No new verified mentions.
- **This run:** Green "new" tags + "Show only new mentions" toggle in the all-mentions table (`TNEW`, `#tblNew`, reuses `SEEN`/`NK`). Next ideas: primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i).

## Scout notes (2026-10-17 ~09:30 UTC)
- **News:** No new verified company-promotion mentions Oct 16–17 (CBD video resurfacing, Strive ASST preferred, Public Citizen PAC report, Trump $1 coin, MRNA rally, QQQ pullback).
- **This run:** "Mentioned more than once" panel (`repeats(sel)`, `#secRep`, Jump-to entry): repeat assets, result since first mention, price move by each later mention. Next ideas: an insights bullet summarising repeat mentions; option to count only the first mention of each asset in averages (like the post dedupe toggle); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i).

## Scout notes (2026-10-17 ~09:35 UTC)
- **News:** X news sweep: Oct 14 Truth Social black-and-white leaders photo, resurfaced Sep 2025 CBD video, Public Citizen PAC report, Dell $6.25B children's accounts, $TRUMP memecoin trader story (unverified), ABC Anduril correction, Paxton/Cornyn posts. None is a company-promotion mention. No new verified mentions.
- **This run:** "Repeat mentions" insights bullet (first-mention-only vs all-mentions held-to-date comparison; links to `#secRep`). Next ideas: optional "Count only the first mention of each asset" toggle across all stats (like the post dedupe); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i).

## Scout notes (2026-10-17 ~09:40 UTC)
- **News:** X news sweep: Oct 14 leaders photo, resurfaced Sep 2025 CBD video, Public Citizen PAC report, Dell $6.25B children's accounts, $TRUMP memecoin trader story (unverified), ABC Anduril correction, Paxton/Cornyn posts. None is a company-promotion mention. No new verified mentions.
- **This run:** "Count only the first mention of each asset" toggle (`FIRST`, `FM()`, `#firstOnly`, `#firstN`; applied to `sel` and the per-group `base` sets; repeats panel and the Repeat-mentions insight still use the unfiltered `SEL0`). Next ideas: primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i); remember filter choices in the URL hash so filtered views are shareable.

## Scout notes (2026-10-17 ~09:50 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Treasurer's Trump $1 coin, Nebius −25% week, GameStop 52-week high, Moderna insider sale, Anthropic/Blackstone chip financing. None tied to a Trump/family/admin company comment. No new verified mentions.
- **This run:** Shareable filtered views (`qsSync()`, `QK`, query params who/cat/type/bm/post/first, `#fLink` copy button; ticker select keeps `location.search`). Next ideas: the Quick takeaway's group comparison ignores the Who filter (says 'Across all groups' even when only Trump is selected; reword or note it); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i).
- **This run:** Quick takeaway's group sentence now says when it sets the Who filter aside and where the chosen group ranks (`takeaway()`). Next ideas: primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i); check other summary sentences (insights bullets) for the same filter-ignoring wording.

## Scout notes (2026-10-17 ~10:00 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Trump $1 coin, $TRUMP memecoin trader story (unverified), Nebius/CoreWeave AI-debt selloff, GameStop 52-week high, Moderna insider sale, WH AI sauna image. None tied to a Trump/family/admin company comment. No new verified mentions.
- **This run:** "By who's talking" insights bullet now flags when it sets the Who filter aside and says where the picked group(s) rank (`rk` in `insights()`). Other insights bullets checked: they use the filtered `sel`/`ok`; the Repeat-mentions bullet uses `SEL0` (pre first-mention toggle, by design, already stated). Next ideas: primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i).

## Scout notes (2026-10-17 ~10:10 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Trump $1 coin, CoreWeave/Nebius/IREN AI-debt selloff, GameStop 52-week high, Anthropic–Blackstone $60B chip financing. None tied to a Trump/family/admin company comment. No new verified mentions.
- **This run:** Prices-as-of header line (`prices_asof` in data.json from `_spx`/BTC-USD last dates; `#pxAsof` under `#gen`). Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i); a local check script for page errors + private-content guard (#16).
- **This run:** Pre-publish check script (#16, `check.py`, wired into publish.sh; `--live` for the published site). Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i).

## Scout notes (2026-10-17 ~10:30 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video, Trump $1 coin, CoreWeave/Nebius/IREN AI-debt selloff, Anthropic–Blackstone $60B chip financing, Trump Greenland rally line. None is a company-promotion mention. No new verified mentions.
- **This run:** "New here? How to read this page" guide (`#guide` details box before `#take`, `tmt_guide_v1` localStorage, `#guideN` live counts, `data-go` links via `goSec`; first TOC entry). Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); China tariff pause expiry Nov 10 2026 watch; TAE S-4 vote milestone (#12i); run check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~10:35 UTC)
- **News:** X news sweep: Trump $1 coin, Public Citizen PAC report, ABC Anduril correction, Dell children's accounts, GameStop CEO buys, Oracle rally, AP-NORC poll on Trump's business focus. None is a company-promotion mention. No new verified mentions.
- **Source checks:** US–China truce extension to Jan 10 2027 announced Sep 23 (Politico/NBC) but some US measures still legally lapse Nov 9–10 (BKL, chinaprospect.com) — replaces the old "Nov 10 tariff pause expiry" idea. DJT EDGAR: latest filing is DEL AM Oct 2 2026; no EFFECT/424B3 yet, no vote date. Truth API SDNY 1:26-cv-06867: Justia docket through Oct 9 shows decision reserved, no ruling (an unverified blog says answer due Oct 30; not used).
- **This run:** "Coming up: dates to watch" panel (`WATCH` const, `watchPanel()`, `#secWatch`/`#watchL`, TOC entry; `@ptr` item computes latest mention + 45 days). Re-check each item every few runs and update `WATCH` when an S-4 EFFECT notice, a Truth API ruling, or a formal truce notice appears. Next ideas: per-ticker feeds (#13, would need many push calls); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~10:40 UTC)
- **News:** X news sweep (12h): resurfaced 2025 CBD video, Trump $1 coin, Todd Gurley at Dalton GA rally, Rubio "America First" interview, Ticktin martial-law Axios story. None is a company-promotion mention. No new verified mentions.
- **This run:** "Best and worst calls so far" panel (`bestWorst(ok)`, `#secBW`/`#bwL`/`#bwCap`, TOC entry; mentions ≥30 days old, top/bottom 5 by excess to date vs `BM`; crypto ids shortened in labels). Lookup marker shapes were already in `tkKey` (12e "mention the marker shapes" is done). Next ideas: optional "per post" view in best/worst when the dedupe toggle is on; per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16, needs workflow-scope push).


## Scout notes (2026-10-17 ~10:45 UTC)
- **News:** X news sweep (12h): resurfaced 2025 CBD video, Trump $1 coin, Nebius/CoreWeave/IREN AI-debt selloff, GameStop 52-week high, Moderna insider sale, Anthropic–Blackstone $60B debt. None is a company-promotion mention. No new verified mentions.
- **This run:** Best/worst panel groups by `post` when DEDUP (`G` map, items `{r,rs,ex}`, "one post, N assets averaged" tag, caption counts posts). Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16, needs workflow-scope push); re-check WATCH items (S-4 EFFECT, Truth API ruling).

## Scout notes (2026-10-17 ~10:55 UTC)
- **News:** X news sweep (12h): resurfaced 2025 CBD video, Trump $1 coin, CoreWeave/Nebius/IREN AI-debt selloff, Moderna insider sale, Anthropic–Blackstone $60B debt, Greenland rally line. None is a company-promotion mention. No new verified mentions.
- **This run:** Plain-English lead for the Congress trades panel (`congCap(sel,rows)` before the count line in `cong()`; party split by member, before/after, same-direction count using `category=='Company criticism'` as negative, smallest-band count, earlier trades filed on/after comment day). Sections still without an "In plain English" lead: coverage notes (`#tEx`) and the index matrix (`#secMx`). Next ideas: those two captions; per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16, needs workflow-scope push); re-check WATCH items.


## Scout notes (2026-10-17 ~11:00 UTC)
- **News:** X news sweep (12h): Trump $1 coin, Nebius/IREN selloff, SOXX record nine-day losing streak, Moderna insider sale, Greenland rally line, Dalton rally (Gurley). Lead to verify: X summary says Trump signed an EO late Oct 16 waiving parts of the 'Sanctioning Russia and Iran Act of 2026' (500%/100% tariffs); check whitehouse.gov / Federal Register before adding as a policy-event line (`PEV`) or a Dates-to-watch item. No new verified company mentions.
- **This run:** Coverage notes plain-English lead (`#exCap`, `EXK` reason map, `kind` field in exclusions.json, new Reason column in `#tEx`). Every main section now has an 'In plain English' lead. Next ideas: verify the Russia sanctions EO lead; per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16); re-check WATCH items.

## Scout notes (2026-10-17 ~11:05 UTC)
- **News:** X news sweep (12h): resurfaced 2025 CBD video, Trump $1 coin, CoreWeave −25% week, WH AI sauna image, FL governor endorsement. No new verified company mentions.
- **Source check:** Russia sanctions EO lead VERIFIED on whitehouse.gov (Oct 16 2026, 'Implementing the Lindsey O. Graham Sanctioning Russia and Iran Act of 2026'; waives §112/113 duties and §102(d) sanctions; CNBC/Politico/CBS). Added as PEV #9. Possible follow-up: Oct ~9 Russian diesel sanctions easing (CBS mentions it) only after finding the official OFAC/WH text.
- **This run:** PEV entry for the Graham Act waiver (timeline line 9 + ticker-lookup line, key text). Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16); re-check WATCH items.

## Scout notes (2026-10-17 ~11:10 UTC)
- **News:** X news sweep (12h): resurfaced 2025 CBD video, Trump $1 coin, CoreWeave/Nebius/IREN AI-debt selloff, Moderna insider sale, GameStop high, Greenland rally line. No new verified company mentions. EDGAR: DJT latest filing still DEL AM Oct 2.
- **Source check:** SDNY 1:26-cv-06867 on CourtListener (docket 74637796): Oct 13 order (Dkt 75) denied stay of answer deadline but extended it Oct 16 → Oct 30 2026; no PI ruling yet. WATCH item now dated 2026-10-30. Re-check after Oct 30 for the answer/motion to dismiss and the PI ruling.
- **This run:** Truth API WATCH item + panel sentence. Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~11:20 UTC)
- **News:** X news sweep (12h): resurfaced 2025 CBD video, Trump $1 coin, CoreWeave/Nebius/IREN AI-debt selloff, SOXX record nine-day losing streak, Moderna insider sale, VIX +21% Oct 16. No new verified company mentions.
- **This run:** daily close-up chart in the ticker lookup (#10). Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16); re-check WATCH items.

## Scout notes (2026-10-17 ~11:30 UTC)
- **News:** X news sweep (12h): resurfaced 2025 CBD video, Trump $1 coin, CoreWeave/Nebius/IREN AI-debt selloff, H-1B tourism row. No new verified company mentions.
- **Backlog hygiene:** #14 "new since your last visit" highlight is already shipped (`SEEN`, `tmt_seen_v1`); drop it from Next lists.
- **This run:** industry fund line on the daily close-up (#10). Next ideas: per-ticker feeds (#13, many files; maybe one `feed-tickers.json` keyed by ticker instead); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16); mention marker shapes in the lookup caption (#12e).

## Scout notes (2026-10-17 ~11:40 UTC)
- **News:** X news sweep: resurfaced Sep 2025 CBD video, Public Citizen PAC report, Doral photo row, Paxton/Cornyn posts, ABC Anduril correction. The CBD video was re-judged: no company named but it is a sector call (same rule as magnets), with a sourced next-day rally (Reuters/Bloomberg/Guardian).
- **This run:** ADDED `BASKET:CANNABIS` (Sep 28 2025, trumpstruth 33128, orig_url status 115283887618990920; MSOS/TLRY/CGC/CRON/ACB; Quiver: no trades in window). Rule going forward: a post or remark promoting a product class whose listed stocks moved on it (sourced) counts as a Sector/theme call even with no company named. Other possible theme leads to verify the same way: Oct 14 2026 Bullhead City copper line (theme only; check for a sourced copper-stock move), Alaska LNG offtake (Oct 14). Next ideas: per-ticker feeds (#13); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~11:45 UTC)
- **News:** X news sweep (12h): resurfaced Sep 2025 CBD video (already tracked), Trump $1 coin (US Treasurer Brandon Beach video; a US Mint collectible, not a listed asset), WH AI sauna image, Rubio "America First", Farcaster sale. No new verified company mentions.
- **This run:** "Recently added to this page" panel (#14; `_site_updates()` in update.py reads CHANGELOG `## date` + bold headlines, skips watchlist/private text; `data.updates`; `updPanel()`, `#secUpd`, TOC "Recently added"). Keep CHANGELOG headlines short and plain since they are now public. Yahoo download for ticker X fails (delisted after the Nippon Steel deal); check whether an X mention needs a last-close fallback. Next ideas: per-ticker feeds (#13, one `feed-tickers.json`); primary OGE Aug 2026 PDF pass (#6); more verified criticism leads (#7); run check.py in GitHub Actions (#16); Bullhead City copper theme lead (verify a sourced stock move first).

## Scout notes (2026-10-17 ~11:55 UTC)
- **This run:** renamed-listing aliases (data gap): `price_ticker` + `ticker_note` + `ticker_src` fields in mentions.json; update.py `ALIAS` downloads the current symbol and copies it to `px[old ticker]`. TZUP→DTCX (Dec 16 2025, Nasdaq ECA2025-687), ALTS→AIFC (Apr 29 2026, 8-K ex99-1). Table tag "now X" and lookup "Ticker change" line. Thumzup Jul 9 2025 date re-verified (SEC filing that day; Decrypt: closed $9.50, −23%). U.S. Steel `X`: Yahoo/Nasdaq have no history; Stooq needs a browser JS check (not used). Leave unpriced unless a clean free source appears. Next ideas: check sectors for DTCX/AIFC (Yahoo profile now reflects the new businesses, so probably keep them out of sector comparison); Quiver congressional check for TZUP/ALTS windows; per-ticker feeds (#13); OGE Aug 2026 PDF pass (#6); check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~12:00 UTC)
- **News:** X news sweep (12h): CBD video (tracked), Trump $1 coin (not a listed asset), CoreWeave/Nebius/IREN AI-cloud selloff, GameStop high — no Trump company comments.
- **This run:** Quiver congressional check for TZUP/DTCX and ALTS/AIFC: no activity on any of the four pages (coverage note in update.py + sectors.json `_note` updated). Next ideas: per-ticker feeds (#13, one `feed-tickers.json`); OGE Aug 2026 PDF pass (#6); check.py in GitHub Actions (#16); Bullhead City copper theme lead; House Clerk direct cross-check for TZUP/ALTS windows (#1, Quiver can miss filings).

## Scout notes (2026-10-17 ~12:05 UTC)
- **News:** X news sweep (12h): CBD video (tracked), Trump $1 coin, WH AI sauna image, Dalton rally Greenland line. No new verified company mentions. whitehouseticker.com returned 404 to WebFetch (try curl/browser next time).
- **Competitor idea:** trumptrack.app lists congress.gov signed bills as a mention source (bills that name companies). Possible future source for #2 discovery.
- **This run:** PEV entries for Section 232 steel/aluminum 50% (Jun 3 2025) and copper 50% (Jul 30 2025), both verified on whitehouse.gov proclamation text; `pevLv` two-row label stagger replaces the ±7px `pevOff` (now a no-op). Next ideas: Bullhead City copper theme lead; House Clerk direct cross-check for TZUP/ALTS windows (#1); OGE Aug 2026 PDF pass (#6); check.py (non-browser part) in GitHub Actions (#16).

## Scout notes (2026-10-17 ~12:15 UTC)
- **News:** X news sweep (12h): Trump $1 coin, Nebius/IREN/CoreWeave selloff, GameStop high, Dalton rally Greenland line, CBD video (tracked). No new company comments besides the rally lead below.
- **This run:** Bullhead City lead resolved. Oct 14 2026 rally named companies directly: ADDED `IE` (Ivanhoe Electric, $1B copper project approval) and `TSM` (TSMC, $265B) as Company praise; sources KTAR + Washington Times, timing from UCSB pool report #5 (spoke from 1:21 PM MST = 4:21 PM ET → after_close, entry Oct 15). Resolution Copper (Rio Tinto 55% / BHP 45% JV) → exclusions.json. New peer ETF `COPX` in sectors.json. Quiver: TSM Cisneros purchase Sep 22 2026 (filed Oct 12) added to congress.json; IE none. committees.json related['TSM'] = NVDA's list. Rally remarks are a rich source: check other Oct 2026 midterm rally transcripts (Dalton GA Oct 16, the evening Oct 14 indoor rally in pool report #11) for named companies. Next ideas: those rally transcripts; House Clerk direct cross-check (#1); OGE Aug 2026 PDF pass (#6); check.py in GitHub Actions (#16).
- Ops note: run push_files batches one at a time; parallel batches race ("not a fast forward").

## Scout notes (2026-10-17 ~12:30 UTC)
- **News:** X news sweep: Public Citizen $210M PAC report, resurfaced CBD video (tracked), Paxton/Cornyn posts, ABC Anduril correction. No new company comments besides the rally below.
- **This run:** Dalton GA Oct 16 rally transcript (trump-archive.com item 9429da01…, Singju Post) checked. ADDED `UCB.BR` (UCB $2B Gwinnett biologics plant) and `PIRC.MI` (Pirelli $1.2B Rome GA; Trump said 1,900 jobs, sources say ~1,000) as Company praise; after_close (pool report 4: took stage 4:24 PM ET) → entry Mon Oct 19, so both unpriced until then. New plain status for comments after the latest close (update.py `e is None` branch keeps the note). Exclusions: Hyundai Transys (private), Lilly/Pfizer/Merck "coming back" (notcall). Quiver: UCBJY last trade Sep 23 2025 (outside window); PPAMY/PLLIF none. Next ideas: re-run on Mon Oct 19 evening to confirm UCB/Pirelli priced; Oct 14 evening indoor rally (pool report #11) transcript; House Clerk direct cross-check (#1); OGE Aug 2026 PDF pass (#6); check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~12:45 UTC)
- **News:** X news sweep (12h): CBD video (tracked), Trump $1 coin, Nebius −25% week (director buy), Newsmax interview (Zelensky, Netanyahu), Rose Garden health joke. No new company comments.
- **This run:** Kalispell MT Oct 14 evening rally (trump-archive.com item 862d49d3…; pool #11 start 7:31 PM MDT = 9:31 PM ET) read in full: no scoreable mentions. Coverage notes added: Janicki Industries (private; janicki.com, news.mt.gov), Fannie/Freddie $3B Montana mortgages (policy, notcall), Colstrip + lumber tariff (notcall). Lead for later: Trump's Fannie/Freddie IPO remarks ("We're thinking about an IPO... It's not a rush", reported Sep 2026, NAMU/CrossGov) could be a company mention for FNMA/FMCC (OTC) if a primary transcript and date are found; also check rally transcripts for Oct 15–17 (trump-archive.com/day/...). Next ideas: re-run Mon Oct 19 evening to confirm UCB/Pirelli priced; House Clerk direct cross-check (#1); OGE Aug 2026 PDF pass (#6); check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~12:50 UTC)
- **News:** X news sweep (12h): Nebius −25% week, GameStop 52-week high, CoreWeave debt selloff, Trump $1 coin, Russia sanctions waiver EO (already PEV #9), Rattner factory-spending chart citing the Oct 12 Youngstown rally.
- **This run:** Youngstown OH Oct 12 rally (trump-archive.com item e62f93c2…; UCSB pool reports Oct 12, note #4: began speaking 7:23 PM ET → after_close, entry Oct 13). ADDED `KMB` (Kimberly-Clark $800M Warren plant, announced May 1 2025), `VK.PA` (Vallourec $48M Youngstown, Nov 10 2025) and `CLF` (DOE $500M award for Middletown Works, Aug 21 2026) as Company praise. sectors.json: KMB → XLP; CLF → XLB/SLX; VK.PA skipped (Paris, EUR). Quiver: KMB/CLF/VLOWY/VLOUF no trades in window. Exclusion: Lilly/Merck/Pfizer general line + Cleveland submarine repair center (government). Other October rallies to check the same way: Dayton OH (early Oct, Trump mentioned "last week" in Youngstown), plus trump-archive.com/day pages Oct 1–11. Next ideas: those rallies; Fannie/Freddie IPO remarks lead; re-run Mon Oct 19 evening for UCB/Pirelli; House Clerk direct cross-check (#1); OGE Aug 2026 PDF pass (#6).

## Scout notes (2026-10-17 ~12:55 UTC)
- **News:** X news sweep (12h): Trump $1 coin, CBD video resurfacing (tracked), Nebius/IREN/CoreWeave AI-cloud selloff, SOXX nine-day losing streak, GameStop high, Musk $158M to Paxton super PAC. No new Trump company comments.
- **This run:** Oct 1 Peterbilt plant tour, Denton TX (trump-archive.com item 0c2b68a3…; UCSB pool report Oct 1 #8: remarks began 4:45 PM CDT = 5:45 PM ET → after_close, entry Oct 2). ADDED `PCAR` (PACCAR/Peterbilt) as Company praise; sectors.json PCAR → XLI (Yahoo: Farm & Heavy Construction Machinery; no peer ETF). Expansion verified via denton.city ($59M PACCAR upgrades) and FreightWaves Oct 2 2026. Quiver: no PCAR trades in window (latest Armstrong Mar 27 2026).
- **October speeches not yet read for company names** (trump-archive.com/day/2026-10-DD): Oct 1 Durant OK rally (8d40d6f5), Oct 2 Mobile AL rally (873f725e; earlier lead lists Peterbilt, Mercedes, U.S. Steel, Eli Lilly, ArcelorMittal — verify against this transcript), Oct 3 Vandalia OH rally (0fe892bb, this is the "Dayton" rally), Oct 5 Grand Island NE (2d2c7290), Oct 6 Maryland military shipyard announcement (dc38c38f, likely names a shipbuilder: high priority), Oct 7 Trump Accounts remarks (7876675c, may name corporate contributors) and San Antonio rally (7d47d21c), Oct 9 Syracuse NY rally (761ac877, Micron already tracked: check for a repeat), Oct 10 Clarksville TN (4864d448). Next ideas: those speeches; Fannie/Freddie IPO lead; Mon Oct 19 UCB/Pirelli re-run; House Clerk cross-check (#1).

## Scout notes (2026-10-17 ~13:05 UTC)
- **News:** X news sweep: Trump $1 coin, Public Citizen $210M PAC report, ABC News corrected Anduril/1789 Capital story (used, corrected version only), Dell Trump Accounts gifts, CBD video (tracked). No new Trump company comments.
- **This run:** Oct 6 Sparrows Point shipyard speech (trump-archive.com item dc38c38f…; UCSB pool reports Oct 6, travel pool #3: took stage 4:02 PM ET → after_close). ADDED `042660.KS` (Hanwha Ocean; Philly yard owned 60% Hanwha Systems 272210.KS / 40% Hanwha Ocean per JoongAng Daily) as Company praise, entry Oct 7. Exclusions: Anduril Arsenal-2 + 40% taxpayer stake (private; 1789 Capital context from ABC corrected story id 137143004), Hadrian + Saronic (private), Peterbilt repeat + Lilly/Merck/Pfizer general line (notcall). sectors.json `_note` lists 042660.KS as skipped (Seoul, KRW).
- **Remaining October speeches to read:** Oct 1 Durant OK (8d40d6f5), Oct 2 Mobile AL (873f725e), Oct 3 Vandalia OH (0fe892bb), Oct 5 Grand Island NE (2d2c7290), Oct 7 Trump Accounts remarks (7876675c; Dell is in the news for Trump Accounts gifts: check whether DELL is praised) and San Antonio (7d47d21c), Oct 9 Syracuse (761ac877), Oct 10 Clarksville TN (4864d448). Idea: 1789 Capital portfolio companies that are public (e.g. PsiQuantum is private) could get a family-linked context row if a verified source lists them.

## Scout notes (2026-10-17 ~13:15 UTC)
- **This run:** Oct 7 San Antonio rally (trump-archive.com item 7d47d21c…; UCSB pool reports Oct 7, travel pool #5: took stage 6:06 PM CDT = 7:06 PM ET → after_close, entry Oct 8). ADDED second `TM` (Toyota $3.6B San Antonio second line / Tacoma from Mexico, announced Jul 6 2026; Toyota pressroom + global newsroom + gov.texas.gov) as Company praise. Quiver TM: none in window (latest Armstrong Mar 30 2026). Oct 7 Trump Accounts remarks (7876675c) read: Dell couple's personal gift + Uber/Intel/NVIDIA/Steak 'n Shake contributor list → exclusions (notcall); rally Goya greeting / unnamed gas plant / Lilly-Merck-Pfizer → exclusions.
- **Remaining October speeches to read:** Oct 1 Durant OK (8d40d6f5), Oct 2 Mobile AL (873f725e), Oct 3 Vandalia OH (0fe892bb), Oct 5 Grand Island NE (2d2c7290), Oct 9 Syracuse (761ac877), Oct 10 Clarksville TN (4864d448). Also the Oct 7 News 4 San Antonio interview (3 min, low priority). Idea: "natural gas power plant deal announced last week" (≈Sep 30–Oct 3) — find the official announcement; if it names a listed company, check whether Trump praised it.

## Scout notes (2026-10-17 ~13:25 UTC)
- **This run:** Oct 2 Mobile AL rally (trump-archive.com item 873f725e…; UCSB pool reports Oct 2, travel pool #5: walked out 6:28 PM CDT = 7:28 PM ET → after_close, entry Mon Oct 5). ADDED `LLY` (Huntsville $6B, Dec 9 2025; specific project + "great company", unlike the general Lilly/Merck/Pfizer line), `MBG.DE` (Tuscaloosa $4B through 2030, Mar 31 2026; Frankfurt, EUR) and `MT` (Calvert $1.2B NOES, Feb 6 2025) as Company praise. sectors.json: LLY → XLV/IHE, MT → XLB/SLX, MBG.DE skipped. Quiver: LLY (latest Newhouse Jul 10 2026), MT (latest Armstrong Mar 30 2026), MBGYY/MBGAF/DDAIF none in window. Exclusions: U.S. Steel Birmingham $475M (delisted), Fannie Mae office move (policy), Cherokee AL submarine facility + Mobile Bay cutters (no company named). Lead: "Cherokee, Alabama" submarine facility — find which company runs it (possibly a listed shipbuilder supplier) before deciding anything.
- **Remaining October speeches to read:** Oct 1 Durant OK (8d40d6f5), Oct 3 Vandalia OH (0fe892bb), Oct 5 Grand Island NE (2d2c7290), Oct 9 Syracuse (761ac877), Oct 10 Clarksville TN (4864d448). Next ideas: those speeches; Fannie/Freddie IPO lead; Mon Oct 19 UCB/Pirelli re-run; House Clerk cross-check (#1).
- Ops note: back-to-back push_files commits can make the last Pages deploy fail ("in progress deployment"); after pushing, check the latest Deploy Pages run and re-run it if it failed, then confirm the live page has the new data.

## Scout notes (2026-10-17 ~13:35 UTC)
- **News:** X news sweep (12h): Trump $1 coin, CBD video (tracked), Nebius/CoreWeave AI-cloud selloff, Texas Senate race. No new Trump company comments.
- **This run:** Oct 3 Vandalia OH rally (trump-archive.com item 0fe892bb…; UCSB pool reports Oct 3, travel pool #4: took stage 7:45 PM ET, Saturday → entry Mon Oct 5). ADDED second `STLA` (Toledo ~$400M midsize truck, 900+ jobs, Stellantis press release Oct 14 2025) as Company praise. Quiver STLA: none in window (latest Armstrong Mar 30 2026). Exclusions: Electra $850M Springfield (private; electra.aero + Ohio governor Jul 21 2026), Bayer aspirin repeat (same-evening post already scored), "big oil companies".
- **Remaining October speeches to read:** Oct 1 Durant OK (8d40d6f5), Oct 5 Grand Island NE (2d2c7290), Oct 9 Syracuse (761ac877), Oct 10 Clarksville TN (4864d448). Next ideas: those speeches; Fannie/Freddie IPO lead; Mon Oct 19 UCB/Pirelli re-run; House Clerk cross-check (#1).

## Scout notes (2026-10-17 ~13:45 UTC)
- **News:** X news sweep: Public Citizen $210M PAC report, CBD video (tracked), Lutnick trade-deal event, Moderna Nasdaq-100 re-entry. Leads: Economic Innovation Group poll (Oct 13 2026) says the administration has taken stakes in 36 companies since mid-2025 ($19–24.5B; e.g. Intel 10%, MP Materials 15%) — a possible source list for a public 'government equity stakes' panel (#3; verify each stake against the company 8-K or agency release). White House Oct 12 achievements graphic names a $6.6B shipyard and Becton Dickinson $19B (BDX Oct 5 already tracked); check whether the graphic was posted by Trump's own account before scoring anything.
- **This run:** Oct 9 Syracuse rally (trump-archive.com item 761ac877…; UCSB pool reports Oct 9, notes 4/5: onstage 8:11 PM ET, speaking 8:13 PM → after_close, entry Mon Oct 12). ADDED second `MU` (Micron $100B Clay NY, Oct 4 2022 press release) as Company praise. Exclusion: Toyota repeat + unnamed NYSE→TXSE companies.
- **#1 data gap FOUND and FIXED:** earlier Quiver parses skipped rows whose asset-type cell is "None" (Khanna, McCaul, Adam Smith, Fleischmann rows). Re-parsed every US stock/ETF window (/tmp/qcheck.py approach: parse every <tr> with Purchase/Sale, match on member last name + date + type) and added 30 trades (79 → 109). Members added to committees.json from /tmp/legislators-current.yaml + committee-membership-current.yaml. False positives to ignore when re-running: "Sale (Partial)"/"Sale (Full)" vs stored "Sale", and "Kean Jr" vs "Kean Jr.". **Still to do:** the same re-check for sector-basket components and non-US tickers' ADR symbols (e.g. UCBJY, TOYOF), and House Clerk direct cross-check.
- **Remaining October speeches to read:** Oct 1 Durant OK (8d40d6f5), Oct 5 Grand Island NE (2d2c7290), Oct 10 Clarksville TN (4864d448). Next ideas: those; insights text may need a line on Khanna's frequent managed-account trading so readers don't over-read his overlap count (verify the managed-account fact from his filings first); Fannie/Freddie IPO lead; Mon Oct 19 UCB/Pirelli re-run.

## Scout notes (2026-10-17 ~13:55 UTC)
- **This run:** read the last three unread October speeches. Oct 1 Durant OK (8d40d6f5): no scoreable mention; exclusion note (unnamed Inola aluminum smelter = EGA 60% / Century Aluminum CENX 40%, Trump named neither; Harold Hamm/Continental private since Nov 22 2022 per SEC; Peterbilt repeat; unnamed Texas gas plant). Oct 5 Grand Island NE (2d2c7290; pool secondary note 4: stage 6:25 PM CDT = 7:25 PM ET, after_close): ADDED `NB` (NioCorp Elk Creek; feasibility capex ~$1.85B vs Trump's $2B; EXIM Oct 15 letter of support) → sectors XLB/REMX; BDX repeat → exclusion. Oct 10 Clarksville TN (4864d448; pool note 4: speaking 3:18 PM CDT, Saturday): ADDED second `GM` (Spring Hill $275M, GM newsroom Jun 24 2026) and `010130.KS` (Korea Zinc $6.6B/740 jobs, TNECD Dec 15 2025; skipped for sectors, KRW); FedEx/Fred Smith anecdote → exclusion. Quiver: NB none listed; GM latest Khanna Apr 13 2026.
- **All October rallies on trump-archive.com are now read.** Next ideas: speeches/remarks for late September (trump-archive.com/day/2026-09-DD) the same way; CENX as a possible government-backed project lead only if Trump names Century; Fannie/Freddie IPO lead; Mon Oct 19 UCB/Pirelli re-run; ADR re-check for sector baskets (#1); Khanna managed-account context line (verify first).

## Scout notes (2026-10-17 ~15:05 UTC)
- **News:** Business Insider on Truth API / early access (already tracked); Kalshi October "what companies will Trump say" markets show SpaceX, Paramount, Toyota, AMD, Meta, IBM, Amazon, Intel, Micron already resolved Yes (many already on this page). DJT / Truth Social traffic stories continue; no new Oct 17 company-promotion posts found this sweep.
- **Fannie/Freddie IPO lead:** still no finishable primary. June 2026 Air Force One "We're thinking about an IPO… It's not a rush" (HousingWire/CNN) is policy talk, not company praise of FNMA/FMCC. Sep 7–8 Truth Social "Great American Mortgage Corporations" videos are housing-advocacy rebrand posts (trumpstruth.org/statuses/41631), not an IPO announcement — leave as coverage note only if revisited, do not score.
- **Peers:** trumptrack.app / TipRanks / trumpstonks / Capitol Trades / Quiver unchanged for finishable UX this sweep. whitehouseticker.com previously 404'd.
- **This run:** late September trump-archive speeches (Sep 28 steel, Sep 29 AI gaggle, Sep 30 LNG). ADDED NEE + second NVDA; private/notcall coverage notes for Mesabi/Essar, Westinghouse/Lewis/Glenfarne, Korean package, OpenAI ID. Design pass not due (only 1 CHANGELOG bullet since the Full redesign).
- **Next ideas:** more late-September day pages (Sep 18–27 speeches not yet read the same way); ADR/sector-basket Quiver re-check (#1); Khanna managed-account plain-English context ONLY if verified from public filings; Mon Oct 19 UCB/Pirelli re-run; clustered/non-overlapping significance (#9); page-size trim (#17); OGE Aug 2026 PDF pass (#6).

## Scout notes (2026-10-17 ~15:25 UTC)
- **News / X:** No new verified company-promotion posts Oct 17. Stories: Nvidia correction / valuation debate (price news; NVDA already tracked), Washington Post ballroom donor list (Apple/Nvidia/Lockheed etc. — donor pledges, not Trump company praise), Youngstown factory-spending chart (already tracked rally), resurfaced ABC Anduril correction (already noted). August 278-T Meta/SpaceX/Nvidia trades already logged under disclosures/#6.
- **Peers:** trumptrack.app still leads OGE 278-T volume; TipRanks/trumpstonks/Capitol Trades/Quiver unchanged for finishable UX this sweep. whitehouseticker.com previously 404'd.
- **Late September day pages (Sep 18–27):** briefs and key transcripts checked. Sep 18 Greenland/H-1B; Sep 19–20 AI branding / Court; Sep 21 Mamdani / press access; Sep 22 UNGA bilats (no scoreable company); Sep 23–24 Boeing praise already tracked (Sep 23 BA; Sep 24 post is the same deal); Sep 25 Xi visit (no company); Sep 26 GM/F/STLA already tracked; Sep 27 Presidents Cup + Anthropic dinner → coverage note (private). No new scoreable mentions.
- **Oct 8 science-medals summit:** VERIFIED (trump-archive 0c7699fd) — ceremonial National Medals naming NVDA/AMD/MSFT/DELL/GOOGL/SpaceX/TSLA. Logged as notcall coverage note (same rule as Trump Accounts contributor list); not scored.
- **This run:** Rankings tab polish — Overview plain-English insight bullet summarizing peer rankings (neutral), guide link to Rankings, Rankings "short version" lead rewritten with top/bottom names and "In plain English". Design pass not due (run 2 of 4 since redesign).
- **Next ideas:** more mid-September day pages (Sep 1–17) if needed; ADR/sector-basket Quiver re-check (#1); Mon Oct 19 UCB/Pirelli re-run; OGE Aug 2026 PDF pass (#6); check.py in GitHub Actions (#16).

## Scout notes (2026-10-17 ~15:35 UTC)
- **News / X:** Lockheed CEO says defense demand is permanent (CNBC; LMT already tracked, not a Trump mention); CBD video resurfacing (tracked); Trump $1 coin (not a stock). Leads: **Oct 16 Dalton GA rally** and **Oct 17 Highland Heights KY rally (Truist Arena, 2 PM ET Saturday)** — read both transcripts on trump-archive.com / UCSB pool reports once posted, as with the October rallies.
- **This run (#1):** Quiver re-parse (`/tmp/qcheck2.py`, handles asset type 'None' and 'Sale (Partial)/(Full)') for all 20 stock/fund sector-basket components (CL=F futures skipped) and US ADR/OTC symbols of all non-US mentions: 0 missing trades. Methods note updated in update.py. Remaining #1: House Clerk PTR XML / Senate eFD direct cross-check; former members.
- **Design pass is due next run** (this was run 3 of 4 since the redesign).

## Scout notes (2026-10-17 ~15:45 UTC)
- **This run: design pass** (run 4 of 4 since redesign): Who chips ordered Trump/Family/Admin with GSY shapes + `.cn` counts, `syncAll()` keeps the All chip and `aria-pressed` in sync (called in chips onclick and at the top of render()); hero captions shortened with `title` tooltips; mobile tab label `.tl-s` "Congress"; tab-row right-edge mask fade; dark tokens `--tx2`/`--hl` fixed (were self-referencing); `#1f2937` dividers/grid → `var(--bd)`/`CV('--bd')`; shots.py desktop now 1280x800. Next design pass due after 3 more runs (count CHANGELOG bullets since this one).
- **Design ideas for later passes:** Overview takeaway paragraph is still ~4 lines on desktop; consider bolding only the first sentence and folding the rest. Insights bullets are long sentences; consider a one-line bold lead per bullet. Remaining hard-coded tag colours (`#22c55e` "new" tags, `.pill.i #374151`) could become tokens.
- **Scout:** no new peer features checked this run (design pass). Still pending: Oct 16 Dalton (already read) / Oct 17 Highland Heights KY rally transcript once posted; Mon Oct 19 UCB/Pirelli re-run.

## Scout notes (2026-10-17 ~15:55 UTC)
- **This run (#2):** Sep 1–17 trump-archive day pages swept (scanner `/tmp/scan.py` + speaker attribution). ADDED `CVX` Sep 2 Rose Garden dinner (pool #10 7:08 PM ET; Trump said $18B, Chevron said >$7B over 5 yrs; Salazar CVX purchase day 0 added to congress.json; CVX → XLE in sectors.json, energy committees in committees.json) and `INTC` Sep 9 RNC Dallas (pool #12 8:09 PM CDT; 4th INTC). Coverage notes: Sep 2 travel-exec list + Netflix/Sarandos; general car-plant lines (Honda/Toyota/GM/F) Sep 2/9/10; Sep 14 Huang call (personal praise; GOOGL repeat). No scoreable: Sep 4 livestock EO, Sep 8 9/11 steel-beam, Sep 10 Medal of Honor (general autos), Sep 16 Gastonia (Starlink), Sep 17 Rose Garden / tele-rally.
- **Next ideas:** Oct 17 Highland Heights KY rally transcript (2 PM ET today) once posted; Aug 2026 day pages the same way; Mon Oct 19 UCB/Pirelli re-run; Honda "big one" plant claim (Sep 2) — verify a specific Honda announcement before scoring; check.py in Actions (#16). Design pass due after 3 more runs (this was run 1).


## Scout notes (2026-10-17 ~16:10 UTC)
- **News / X:** no new Trump company-promotion posts Oct 17 (CBD video resurfacing, Todd Gurley at Dalton, KY rally crowds, Nebius/IREN selloff). Oct 17 Highland Heights KY rally (2 PM ET) still to read once the transcript posts.
- **This run (#2):** August 2026 day pages listed with `/tmp/daylist.py` (anchors with Speech/Remarks/Gaggle/Interview titles; 65 items) and scanned with `/tmp/scan2.py "<speaker>" <uuids>` (fixed speaker split: the old scan.py split at both "Donald" and "Trump", so it silently found nothing). ADDED LAC Aug 5 (after close → Aug 6; earnings Aug 13 in window), MP Aug 7 (before close; Q2 earnings Aug 6 after close confound noted), CLF Aug 21 Admin (Vance + DOE; 10:00 AM ET release). 3 coverage notes. Oct 16 RNC Mar-a-Lago + gaggle: nothing scoreable.
- **Not yet read in August:** interviews (Fox Aug 4/14/30, Punchbowl Aug 6, Root Aug 11, Glenn Beck Aug 26, Michael Cohen Aug 20), gaggles (Aug 2/4/11/14/16/21), Navarro/Bessent/Hassett/Rollins/Leavitt/Miller briefings (Admin). Next: scan those with scan2.py (speaker "Donald Trump" or the official's name).
- **Next ideas:** Oct 17 KY rally; August interviews/briefings; Mon Oct 19 UCB/Pirelli re-run; Honda Sep 2 claim; check.py in Actions (#16). Design pass due after 2 more runs.

## Scout notes (2026-10-17 ~16:30 UTC)
- **This run: design pass** (run 4 of 4): `takeaway()` now renders `out[0]` as `.tkLead` (19px/600, 17px on mobile) and the rest as `.tkRest` (15.5px, `--tx2`); every `insights()` bullet now opens with a bold `<b>Label:</b>` lead (`.ins li>b:first-child` uses `--tx`); new tokens `--new`/`--onnew` with `.tag.nw` replace three inline `#22c55e` styles; `#take`/`#guide` borders and the Rankings warning use `var(--acc)`/`var(--link)`/`var(--r)`. Next design pass after 3 more runs (count CHANGELOG bullets).
- **Design ideas for later passes:** party pills (`.pill.d/.r/.i/.s`) still use fixed colours (fine in both themes, but could be tokens); who-colour legend spans in the guide are fixed by design; consider trimming the insights list (20 bullets) by folding the rarely-read statistical ones into Performance.
- **Scout:** Oct 17 Highland Heights KY rally (2 PM ET = 18:00 UTC) not yet held; read it once the transcript posts. Mon Oct 19 UCB/Pirelli re-run still pending.

## Scout notes (2026-10-17 ~16:40 UTC)
- **Added:** May 21 2026 Commerce/NIST quantum equity-stake letters of intent (IBM, GFS, QBTS, RGTI, INFQ; Admin, Government stake/deal; QTUM peer fund added). Follow-ups: watch for the final agreements (letters of intent only) and the Jun 17 2026 SandboxAQ $500M stake (private, add to exclusions.json if not there); check other 2026 Commerce/DoD/DOE stake announcements (Reuters Jun 17 2026 factbox lists them) against mentions.json.
- **June 2026 sweep (in progress):** scanned Jun 1 CNBC, Jun 3 trade EO, Jun 4 coal, Jun 5 Wisconsin ag roundtable, Jun 22 quantum EO, Jun 23 Mack Trucks, Jun 25 farmers dinner, Jun 29 auto-repair EO. Leads: Jun 23 Eli Lilly "great company" $3.5B Lehigh Valley and "Mack Trucks is doing a great job" (Volvo Group, VOLV-B.ST; govinfo DCPD-202600423; motorcade arrived 2:05 PM ET, need speech start); Jun 22 IBM CEO praise + Trump's "I used to have that stock... I brilliantly sold it when I became president" (coverage note; IBM now tracked via May 21); Jun 23 "a great company" re Nippon Steel/US Steel (retrospective); Jun 5 John Deere right-to-repair line. Still to read: Jun 24 DC rally, Jun 26 Faith and Freedom, gaggles Jun 5/9/17/23, tele-rallies.

## Scout notes (2026-10-17 ~16:55 UTC)
- **Added:** Jun 23 2026 Mack Trucks Macungie speech: `LLY` (Lehigh Valley $3.5B, "great company", 3:07 PM ET, same-day) and `VOLV-B.ST` (Mack Trucks "doing a great job", after Stockholm close, day 0 Jun 24). Two House LLY purchases (Khanna Jun 2, Cisneros Jun 10) added to congress.json. Add VLVLY/VLVLF to the ADR map in /tmp/qcheck2.py on the next Quiver re-check.
- **June 2026 sweep (continuing):** done: Jun 1, 3, 4, 5, 22, 23 (speech), 24 (National Mall rally), 25 (farmers dinner), 29 (auto-repair EO). Still to read: Jun 26 Faith and Freedom speech (75ac3695) and Religious Liberty report (b971ec3c), Jun 23 Air Force One gaggle (58ece353), Jun 24 Capitol gaggles (ce13ccb8, 7fbad722), Jun 9 and Jun 17 gaggles, Jun 17 G7 press conference (2876cc2f), Jun 11 Fox and Friends call-in (a3e3e62c), Jun 18 Axios Show interview (729fab35), tele-rallies. Then May 2026.
- **Scout:** Oct 17 Georgia airport rally (morning, with Todd Gurley; X news) and Highland Heights KY rally (2 PM ET) — read both transcripts when posted. Competitor check this run: X news only (no new tracker features seen).

## Scout notes (2026-10-17 ~17:00 UTC)
- **Added:** Jun 19 2026 Boeing praise (`BA`, new Air Force One remarks, Joint Base Andrews; Juneteenth holiday so day 0 Jun 22; mixed praise with price complaint). VLVLY/VLVLF added to the ADR map in /tmp/qcheck2.py (0 missing).
- **June 2026 sweep: DONE.** Next: May 2026 sweep (use /tmp/daylist.py for days, /tmp/scan2.py "Donald Trump" <uuids>; also scan admin briefings with the speaker's name).
- **Next run is a design pass** (run 4 of 4). Ideas: fold the rarely-read statistical insights into Performance; party pills to tokens.
- **Scout:** Oct 17 Georgia (Dalton-area) and Highland Heights KY rally transcripts not posted yet; read them when they are. /tmp/qcheck.py reports 5 known false positives (Sale vs Sale (Partial/Full) key mismatch; trades are already in congress.json).

## Scout notes (2026-10-17 ~17:05 UTC)
- **This run: design pass** (run 4 of 4): `insights()` now pushes the statistical bullets to `st[]` and renders them into `#insS` (Performance tab, `#secInsS`, after `#cards`; sorted so More than luck / Average vs typical / On the day itself lead); the three appended bullets (pre-move base rates, ordinary days, jumpiness) now target `#insS`. `#insL` shows 12 everyday bullets (4 visible). Clip logic handles both lists (insL 4, insS 3). New tokens `--pD --pR --pI --pS --onP` for party pills. Next design pass after 3 more runs (count CHANGELOG bullets).
- **Design ideas for later passes:** Performance headline cards are 7 across on desktop (consider 4 primary + fold the rest); Overview takeaway on mobile is still long; check the Disclosures tab density.
- **Next data run:** May 2026 speech sweep (/tmp/daylist.py, /tmp/scan2.py); Oct 17 Georgia and Kentucky rally transcripts when posted; Mon Oct 19 UCB/Pirelli re-run.
- **Scout:** no competitor check this run (design pass).

- **May 2026 sweep (started 2026-10-17 ~17:15 UTC):** done May 16–31 (Trump items: May 18 healthcare event 60e41ee1, May 19 ballroom gaggle and picnic, May 20 gaggles and Coast Guard, May 21 EPA refrigerants 96df52dd, May 22 Warsh and Suffern c4a28a1d, May 27 cabinet 1814c4ac, May 28 Lara Trump interview); added MU May 22. Not yet scanned in this half: JD Vance May 18 Kansas City manufacturing speech (3469a194), Vance May 19 briefing (ec04c40e), Bessent May 28 briefing (aeac8705) — scan with the speaker's name. Next: May 1–15 day pages (/tmp/daylist.py, /tmp/scan2.py). Design pass: run 1 of 4 since the last one (next design pass after 3 more runs).

## Scout notes (2026-10-17 ~17:35 UTC)
- **May 2026 sweep:** done May 13–15 (Beijing) and the late-May Vance (3469a194, ec04c40e, 701b9030) and Bessent (aeac8705) items. Added BA May 14 (intraday clip) and V May 14 (aired 9 PM ET, day 0 May 15). Quiver check: use /tmp/qcheck.py (it covers every stock ticker; /tmp/qcheck2.py only covers baskets and ADRs). Do not push in parallel with push_files (second call fails "not a fast forward").
- **Still to read in May 1–12:** May 1 Forum Club speech (6b43c55e) and seniors event (b4631a4f), May 4 Small Business Summit (2d442348) and Hugh Hewitt (28adb215), May 6 UFC Oval remarks, May 8 Mother's Day luncheon (DELL May 8 already tracked), May 11 Rose Garden dinner and maternal healthcare event, May 12 Sid Rosenberg (4a1f6f38), plus gaggles (May 1, 2, 3, 7, 8, 12). Possible lead: other delegation CEOs on the Beijing trip (Tesla, BlackRock, Illumina, Mastercard) only if Trump names them.
- **Design pass:** this was run 2 of 4 since the last one (next design pass after 2 more runs).

## Scout notes (2026-10-17 ~17:40 UTC)
- **May 2026 sweep done** (May 1–31). Added DELL May 1 (Villages, after close). Intel May 1/May 4 repeats in exclusions. No Vance May 5 Des Moines factory speech (0bb6bdbf) scan yet; scan with "JD Vance" next.
- **Next data run:** April 2026 speech sweep (/tmp/daylist.py then /tmp/scan2.py with full UUIDs); Oct 17 Kentucky rally transcript when posted; Mon Oct 19 UCB/Pirelli re-run.
- **Design pass:** this was run 3 of 4 since the last one, so the NEXT run must be a design pass (ideas: Performance cards 7 across → 4 primary; Overview takeaway on mobile; Disclosures tab density).
- **Scout:** peers unchanged (no competitor check this run beyond backlog notes).

## Scout notes (2026-10-17 ~17:45 UTC)
- **This run: design pass** (run 4 of 4): `#cards` on Performance is now 4 cards (`[big, label, small]` with `.card>small`), win/beat rates use the neutral `rt()` formatter (also in `#hcards`), `.cards` min 190px and a 2-column phone grid. Next design pass after 3 more runs (count CHANGELOG bullets).
- **Design ideas for later passes:** Overview takeaway on mobile is still long; check the Disclosures & Congress tab density (long tables, many panels); the Performance lead paragraph could be one line.
- **Next data run:** April 2026 speech sweep (/tmp/daylist.py then /tmp/scan2.py); Vance May 5 Des Moines (0bb6bdbf) with "JD Vance"; Oct 17 Kentucky rally transcript when posted; Mon Oct 19 UCB/Pirelli re-run.
- **Scout:** no competitor check this run (design pass).

## Scout notes (2026-10-17 ~17:55 UTC)
- **April 2026 sweep (started):** Apr 16–30 done; added DELL Apr 16 (Las Vegas, "buy their computer"). The Trump Archive has no April transcripts; use /tmp/scan3.py "Donald Trump" <full uuids> (fetches the Roll Call Factbase transcript linked from each archive item; text saved to /tmp/rc-<id>.txt). Next: Apr 1–15 (/tmp/daylist.py then scan3.py), then Vance May 5 Des Moines (0bb6bdbf) with "JD Vance".
- **Backlog question:** TrumpRx / Most Favored Nation drug-pricing deals announced by Trump (Pfizer Sep 30 2025, AstraZeneca, EMD Serono, Lilly/Novo, Regeneron Apr 23 2026, others) are not tracked. Decide whether to add them as Admin "Government stake/deal" rows (consistent rule: announced at a White House event with the company named, before/after-close timing from pool reports).
- **Quiver check:** /tmp/qcheck.py now shows 5 known false positives (AAPL Capito, DELL Mullin, GOOGL Kean, INTC Peters, NVDA Whitehouse); the two Apr 16 DELL trades were added. Armstrong's DELL row has no eFD `ptr` block yet (the Jul 21 PTR likely covers it; verify before adding).
- **Design pass:** run 1 of 4 since the last one (next design pass after 3 more runs).
- **Scout:** no competitor check this run (time spent on the April sweep).

## Scout notes (2026-10-17 ~18:05 UTC)
- **April 2026 sweep finished (Trump):** Apr 1–15 done; added DASH Apr 13 (McDonald's DoorDash delivery, 12:38 PM ET, intraday). Still unread for April: Vance's Apr 7 Budapest rally/press conference, Apr 8/10 gaggles, Apr 11 Islamabad briefing and Apr 14 Athens GA Turning Point town hall (scan3.py "JD Vance" with full uuids from /tmp/apr1-15.txt), plus Vance May 5 Des Moines (0bb6bdbf).
- **News Oct 16–17:** GlobalFoundries Truth Social stake post already tracked; Georgia UCB/Pirelli/Hyundai video (Rapid Response 47, Oct 17) is the speech already queued for the Mon Oct 19 re-run. Visa's Oct 13 China clearing approval (TipRanks) is useful context for the tracked May 14 Visa mention; consider a follow-up note.
- **Competitor idea:** Hudson Labs' "Trump Bump" list rates each praised company with a confidence level (High/Medium) and a praise type; consider a "how direct was the comment" tag in the Mentions table (collapsed by default).
- **Design pass:** run 2 of 4 since the last one (next design pass after 2 more runs).

## Scout notes (2026-10-17 ~18:15 UTC)
- **Vance done:** April 2026 events (Apr 1, 7, 8, 10, 11, 14) and May 5 Des Moines (0bb6bdbf) read; no stock named; coverage note added for his congressional stock-trading-ban remarks (Apr 14 Athens, May 5 Des Moines).
- **New lead (verify before adding):** Trump on Tesla's Roadster (unveiled Oct 16; Tesla shares +5% per 1news.az citing RBC): "I don't know whether you will see me in this car, but it's quite impressive", said to reporters at the White House. Find the primary transcript (Roll Call Factbase / Trump Archive Oct 16–17) for the date and time vs the close before scoring as TSLA praise.
- **Context:** Oct 17 Truth Social post of S&P 500 5,881 to 7,651 ("The strongest in history!"), index boast, not scored.
- **Design pass:** run 3 of 4 since the last one, so the NEXT run must be a design pass.
- **Daily digest:** sent on the 18:07 UTC run for 2026-10-17; don't send another today.

## Scout notes (2026-10-17 ~18:20 UTC)
- **This run: design pass** (run 4 of 4): flag/who-tag tokens + `gTag()`; mobile takeaway "More detail"; Disclosures tab folds OGE overlaps; chart accents via `CV()`; shorter tab leads. Next design pass after 3 more runs (count CHANGELOG bullets since this one).
- **Design ideas for later passes:** Mentions tab still opens with ticker lookup + full table (consider folding the close-up zoom by default on phones); Rankings chart height (700px) is tall on mobile; leftover chart palette `IC[]` / `GC` hexes are intentional who-colours (keep fixed across themes).
- **Scout (brief):** Oct 17 Highland Heights KY midterm rally happened (Truist Arena / NKU; X news ~18:12 UTC) — transcript not yet checked this run; read next data run. Tesla Roadster "quite impressive" lead still pending primary transcript before any TSLA add. Hudson Labs "Trump Bump" confidence-tag idea still on backlog. Peers unchanged this pass (design-focused).
- **Backlog add:** optional "how direct was the comment" confidence tag (High/Medium, Hudson Labs–style) on Mentions rows, collapsed by default — logged under UX if not already covered.
- **Daily digest:** already sent earlier today; not resent.

## Scout notes (2026-10-17 ~18:30 UTC)
- **Tesla Roadster lead DONE:** verified in the Oct 16 Marine One gaggle (Roll Call Factbase, ~12:58 PM ET via pool reports 9704/9706); added TSLA Oct 16 Company praise. The 1news/RBC "+5%" claim is not borne out by closes (TSLA −2.1% on Oct 16); not used. Re-run the Quiver TSLA check after Oct 23 for trades in the week after.
- **Timing source:** pool.pp.tools (independent White House pool report archive) has dated, timed in-town and travel pool reports; useful when the American Presidency Project hasn't posted a note yet.
- **Next data run:** Oct 17 Highland Heights, Kentucky rally (Truist Arena) once the Trump Archive/Roll Call transcript posts; Mon Oct 19 re-run for UCB/Pirelli day 0.
- **Design pass:** run 1 of 4 since the last one (next design pass after 3 more runs).
- **Daily digest:** already sent today.

## Scout notes (2026-10-17 ~18:45 UTC)
- **March 2026 sweep started:** Mar 16–31 done (Trump transcripts); added MU Mar 26 (The Five, after close) plus a Disclosures entry for Trump's Mar 25 Micron purchase. Exclusions: RTX/LMT Mar 19, Disney/Perlmutter Mar 16, Deere/Case/CAT Mar 27.
- **Top new leads (verified in Popular Information/Mother Jones May 20 2026 and Washington Examiner May 28 2026, still need primary transcripts + timing):** Thermo Fisher (`TMO`) Mar 11 Reading, Ohio plant tour ("It's a great company"; Trump's OGE report lists TMO buys Feb 12, Mar 2 and Mar 11); Apple (`AAPL`) Mar 11 Hebron, Kentucky speech ("Apple, a great company"; AAPL buys Mar 2–25 up to $7.2M); Dell plugs Feb 27 and Mar 9 2026 (not tracked yet; Dell buys Mar 2, Mar 11, Mar 23 too, add to the existing Dell disclosure). Also Jan 6 2026 NVDA/AMD buys before the Jan 13 China chip approval (NOTUS) as a disclosure-context item if there's a matching mention.
- **Next data run:** finish March 2026 (Mar 1–15, starting with Mar 11 TMO/AAPL and Mar 9 Dell); Oct 17 Highland Heights KY rally once its transcript posts (not on the Trump Archive yet at 18:40 UTC).
- **Design pass:** run 2 of 4 since the last one. **Daily digest:** already sent today.

- **This run (#2):** March 2026 sweep finished (Mar 1–15). ADDED `TMO` Mar 11 Thermo Fisher tour (2:50 PM ET intraday) + same-day OGE purchase in disclosures + 3 Khanna trades. Next: February 2026 speech sweep (`/tmp/daylist.py` + `/tmp/scan3.py "Donald Trump" <uuids>`); also check the Washington Examiner / Mother Jones May 2026 'praised within days of buying' list for any other companies not yet tracked. Next run must be a design pass.

- **This run: design pass** (run 4 of 4): Mentions close-up zoom folded on phones (`#tkZW` is now `details.more`, opened by default when `innerWidth>640`), price-key labels shortened and the wrong "solid white line" fixed, timeline/per-month heading subs shortened (legend in `title`), Rankings chart rows 17px on phones. Next design pass after 3 more runs.
- **Design ideas for later passes:** the per-ticker mention table under the lookup (`#tkv`) is very wide on phones (consider card rows or folding sector/peer columns); "All mentions" table could default to fewer columns on phones; Congress tab density check.
- **Scout:** no competitor check this run (design pass). Pending data work: February 2026 speech sweep; Oct 17 Highland Heights KY rally transcript; Mon Oct 19 UCB/Pirelli re-run.

## Scout notes (2026-10-17 ~19:20 UTC)
- **February 2026 sweep started:** Feb 15–28 Trump transcripts done; added DELL Feb 27 Corpus Christi energy speech (after close, day 0 Mar 2; earnings jump the day before noted). Next: Feb 1–14 (`/tmp/daylist.py` then `/tmp/scan3.py "Donald Trump" <uuids>`), plus Vance's Feb 26 Plover, Wisconsin manufacturing speech (fbe8eaf6) and the Feb 25 Vance/Oz fraud remarks (af78cdae).
- **Oct 16 RNC remarks at Mar-a-Lago** read: nothing scoreable. Oct 17 Highland Heights KY rally transcript still not on the Trump Archive at 19:15 UTC.
- **Convention check:** each congressional trade is linked to one mention only (e.g. Khanna's Apr 13 DELL trade sits under May 8, not Apr 16); kept that for Feb 27.
- **Design pass:** run 1 of 4 since the last one (next design pass after 3 more runs). **Daily digest:** already sent today.

## Scout notes (2026-10-17 ~19:35 UTC)
- **February 2026 sweep finished:** Feb 1–13 Trump transcripts done; added GM Feb 2 (Oval Office critical-minerals reserve, after close) and BTU Feb 11 (Champion of Coal event, after close). Exclusions: Ford plant recap, Lilly/AstraZeneca TrumpRx price cuts, John Deere regulation example. Still to read: Vance's Feb 26 Plover, Wisconsin speech (fbe8eaf6) and the Feb 25 Vance/Oz fraud remarks (af78cdae); Vance's Feb 4 Critical Minerals Ministerial (f3f2a9b9).
- **Next data run:** January 2026 sweep (`/tmp/daylist.py 2026-01-{16..31}` then `/tmp/scan3.py "Donald Trump" <uuids>`); check Trump's OGE reports for GM/BTU trades near Feb 2/11 if a source lists them. Oct 17 Highland Heights KY rally transcript still not on the Trump Archive at 19:30 UTC.
- **Design pass:** run 2 of 4 since the last one (next design pass after 2 more runs). **Daily digest:** already sent today.

## Scout notes (2026-10-17 ~19:45 UTC)
- **January 2026 sweep started (Jan 16–31 Trump transcripts done):** ADDED `AAPL` Jan 21 Davos WEF business reception (intraday) and `DE` Jan 27 Clive, Iowa economy speech (after close). Exclusions: Lilly MFN Jan 16 / Cabinet Jan 29, Jan 20 investment roll-call, Toyota Davos aside, Ford plant recaps. Still to read: Jan 1–15 (`/tmp/daylist.py 2026-01-{01..15}` then `/tmp/scan3.py "Donald Trump" <uuids>`); unread Vance Feb items (fbe8eaf6 Plover, af78cdae Feb 25, f3f2a9b9 Feb 4 Critical Minerals) if time.
- **Oct 17 Highland Heights KY rally:** still no speech/remarks transcript on the Trump Archive at ~19:40 UTC (day page shows only Truth Social posts and a Russia-sanctions document). Re-check next data run.
- **Scout (brief):** X news Oct 16–17 still Micron/memory-stock volatility, TSMC earnings, IREN AI-cloud selloff — price news only, no new Trump company-promotion posts. Peers unchanged this pass (data-focused). Optional OGE check for GM/BTU near Feb 2/11 still open if Washington Examiner / Mother Jones list them.
- **Design pass:** this was run 3 of 4 since the last one, so the **NEXT run must be a design pass** (ideas from prior notes: per-ticker mention table on phones; All-mentions fewer columns on phones; Congress tab density).
- **Daily digest:** already sent today; not resent.

## Scout notes (2026-10-18 ~09:30 UTC, daily data-only run)
- **Oct 17 Highland Heights KY rally: DONE** (no Trump Archive/Roll Call transcript yet; used the RSBN livestream captions via yt-dlp, `CQU5WIRXRNQ`, speech starts at stream 05:22:41 = 2:20 PM ET per pool report 7; pool.pp.tools 9727/9728). Added `6690.HK` (GE Appliances/Haier, weekend, day 0 Mon Oct 19). Antheia (private) and other lines → exclusions. Oct 17 MAGA Inc dinner (pool 9735–9738): nothing scoreable. Swap the source to the Roll Call/Trump Archive transcript once it posts.
- **January 2026 sweep: DONE** (Jan 1–15 via `/tmp/scan2.py "Donald Trump" <uuids>`; trump-archive item pages carry the transcript text). Added XOM/CVX/COP Jan 9, XOM criticism Jan 11, F and STLA Jan 13. Roll Call Factbase returns 502 to curl's default UA; use a full Chrome UA string.
- **OGE source:** Quiver's Trump page (quiverquant.com/Donald-Trump-Stock-Trades/) embeds every Trump 278-T trade (Jan 2–Mar 30 2026 so far) as JSON arrays; the May 8 2026 278-T PDF on extapps2.oge.gov is the primary (pdftotext works). Use it to check any new Trump mention in that range for nearby personal-account trades. Not yet checked this way: older 2026 mentions other than DELL/MU/TMO (e.g. GM Feb 2, BTU Feb 11, AAPL Jan 21, DE Jan 27, LLY, INTC).
- **Pending:** Mon Oct 19 re-run so UCB/Pirelli (Oct 16) and Haier (Oct 17) get day 0; TSLA Oct 16 Quiver re-check after Oct 23; Vance Feb items (fbe8eaf6, af78cdae, f3f2a9b9); December 2025 speech sweep next.
- **Remote note:** the repo got a user redesign on Oct 17–18 (template.html, .gitignore; commits dbc9d6e, ece33b8, d967e51). Local template.html/.gitignore were synced from main before rebuilding (old local copy at /tmp/bak-1018/template.local-pre-sync.html). Always compare local vs remote blob SHAs before pushing template.html/index.html.

## Scout notes (2026-10-19 ~09:15 UTC, daily data-only run)
- **No new mentions.** Oct 18 Trump posts, family and cabinet X posts, and X news checked. Musk medal = Oct 8 summit (already excluded).
- **Open-session gotcha:** at ~09:00 UTC Yahoo returns a partial Oct 19 bar for European listings (UCB.BR, PIRC.MI were wrongly "priced" with index excess = raw return). Until update.py drops unclosed sessions itself, run `/tmp/run_update_complete.py` (drops today's non-crypto bars, then runs update.py unchanged) instead of plain `python update.py`, and run check.py + the publish.sh guard lines by hand (publish.sh calls plain update.py). Possible code fix if the user ever asks: in update.py, drop bars dated today unless the exchange has closed.
- **Pending:** next run (Oct 20) should score UCB/Pirelli/Haier (Oct 19 day 0); Oct 17 KY rally transcript swap (Roll Call 502 today); TSLA Oct 16 Quiver re-check after Oct 23; Vance Feb items; December 2025 speech sweep.

## Scout notes (2026-10-20 ~09:20 UTC, daily data-only run)
- **Added 4 mentions:** MRK and BA (Oct 19 Park City, Kansas rally, after close → day 0 Tue Oct 20), BBD-B.TO (KWCH interview + rally "certain air company", softer line after the Sep 7 criticism; day 0 Oct 20), WMB (DOE $42M DPA Constitution Pipeline award, 10:08 AM ET Oct 19, Admin Government stake/deal). Congress +1 (Salazar Sep 24 MRK sale). Exclusions: Musk SpaceX Trump Accounts gift (Trump + Bessent), rally leftovers (drugmaker line, Toyota repeat, credit-card/insurance, biofuel, Mercedes joke, Ruffin), gaggle Starlink answer, Burgum Yellowstone gift thanks, Duffy Alaska rail.
- **Oct 17 KY rally:** Roll Call transcript now posted (`0efa1332`); GE Appliances source swapped. **Haier 6690.HK:** Mon Oct 19 was an HKEX holiday (day after Chung Yeung), so day 0 is Tue Oct 20; it scores on the next run (with MRK/BA/BBD).
- **Pending:** next run scores MRK/BA/BBD-B.TO/6690.HK (Oct 20 day 0); TSLA Oct 16 Quiver re-check after Oct 23; Merck/Boeing/Williams Quiver re-check after the +7d window (Oct 26) and again once filings close; Trump's September OGE 278-T (when public) for MRK/BA/WMB trades near Oct 19; Vance Feb items; December 2025 speech sweep. Quiver name-match quirk: "Thomas H. Kean Jr" vs "Jr." shows as a false 'missing' trade in the recheck script.
- Run used `/tmp/run_update_complete.py` again (European bars open at 09:00 UTC). Published 9247b95 / 4564092 / e3c44c4 / a6632ee; live check passed.

## Scout notes (2026-10-21 ~09:20 UTC, daily data-only run)
- **Added 2 mentions:** `WOLF` (Admin, Department of War OSC $1.5B conditional loan + warrants up to 7.5%, Oct 7 after close, day 0 Oct 8; surfaced by Trump's unnamed Oct 20 Greenville NC rally line) and `AAPL` (Family, Don Jr. "Good for Apple!" quote-post, 7:08 PM ET Oct 20, day 0 Oct 21, scores next run). Congress +1 (Pete Sessions AAPL sale Sep 22). WOLF mapped to Technology/XLK/SMH and MU's committees plus Armed Services.
- **Exclusions:** Sibelco (private, Euronext Expert Market only) and other NC rally lines; fraud event Toyota repeat, SBA video, Oct 21 data-center post; Hegseth/L3Harris "Arsenal of Freedom" quote-posts, Wright/CenterPoint visit, Kushner Trump Accounts thanks.
- **Scored:** MRK/BA/BBD-B.TO/6690.HK now have Oct 20 day 0.
- **Sources:** Roll Call Factbase still 502s (even with a Chrome UA) for new transcripts, but trump-archive item pages carry the full text (`/tmp/scan2.py`). pool.pp.tools gave the rally start (report 9810) and the Sibelco/Pentagon report (9813).
- **Pending:** AAPL Oct 21 day 0 next run; TSLA Oct 16 Quiver re-check after Oct 23; MRK/BA/WMB/AAPL re-check after their +7d windows (Oct 26–27) and when filings close; Trump's September OGE 278-T for MRK/BA/WMB/AAPL trades; Sibelco site/amount if a company or state release follows (still private); Vance Feb items; December 2025 speech sweep. Lead to consider: the OSC has other conditional loan commitments to listed companies (check war.gov releases since Aug 2026 for untracked ones).
- Published 2ab593b / 066a2f2 / c29e387 / 1dfb85a (a parallel push raced, so two batches were re-sent; remote blob SHAs verified against local).

## Scout notes (2026-10-22 ~09:30 UTC, daily data-only run)
- **Added 3 mentions:** `BA` (Admin, Duffy X post on the 737 MAX 10, 1:32 PM ET Oct 21, day 0 Oct 21), `BETA` (Admin, Duffy X post on the FAA market-survey certificate, 6:48 PM ET Oct 21, day 0 Oct 22) and `AAPL` (Trump Truth Social post on the Apple/Perryman titanium deal, 10:29 PM ET Oct 21, day 0 Oct 22). New `who` value "Sean Duffy (Transportation Sec.)". BETA mapped to XLI/ITA and BA's committees.
- **Exclusions:** Pendleton SC rally (Google Maps story, Dell gift) and cybercrime roundtable (Meta/X/Google/Microsoft/IBM law-enforcement help); UK North Sea post, Rapid Response GlobalFoundries repost (Oct 14 already tracked), Melania women's health posts.
- **Truth Social API** (`truthsocial.com/api/v1/statuses/<id>` with a Chrome UA) returns full post text and created_at when trump-archive item pages are empty.
- Published d7f37f6 / f6e1063 / 5a4405c / b3d4f27; live check passed (139 mentions live, 0 errors at 1280px and 390px).
- **Pending:** BETA/AAPL Oct 22 day 0 next run; TSLA Oct 16 Quiver re-check after Oct 23; MRK/BA/WMB/AAPL/BETA re-check after their +7d windows (Oct 26–29) and when filings close; Trump's September OGE 278-T; Vance Feb items; December 2025 speech sweep; OSC conditional-loan lead (war.gov releases since Aug 2026).

## Scout notes (2026-10-24 ~09:30 UTC, daily data-only run)
- **Oct 23 run had stopped early:** it added RTX (Duffy, Oct 22) and BBD-B.TO (Trump, Oct 22 after close), exclusions and the RTX sector/committee mapping locally but never ran update.py or published. This run finished and published them.
- **Added 3 mentions:** `IPI` and `ASIX` (Admin, USDA FIELDS fertilizer selections Oct 22, 1:06 PM ET, day 0 Oct 22; same post) and `AEP` (Admin, DOE $50M DPA Virginia transmission grant Oct 16, 12:23 PM ET; Appalachian Power gets $40M). New `who` value "JD Vance (Vice President) / Department of Agriculture". IPI/ASIX mapped XLB + Agriculture committees; AEP XLU + Energy committees.
- **Lesson:** when a release lists several recipients, check every name for a listing (the Oct 23 check only noted the private TalusAg). Same for DOE SPARK/DPA grid awards: check whether a listed utility's subsidiary is a recipient.
- **Exclusions:** Fort Myers rally/gaggles/WINK interview (Musk/Starlink, Google Maps story, nurses), Rapid Response U.S. Steel (Nippon-owned, unlisted) and aluminum headlines, USDA SPUR loans, Peace Valley (private).
- **Sources:** trumpstruth.org/feed (via www.) works for the post list; truthsocial.com account API is behind Cloudflare. trump-archive.com/day/YYYY-MM-DD lists transcripts; item pages carry full text.
- **Pending:** Trump's Oct 24 Michigan rally transcript; MRK/BA/WMB/AAPL/BETA/RTX re-check after their +7d windows (Oct 26–29) and when filings close; IPI/ASIX/AEP re-check after +7d; Trump's September OGE 278-T; Vance Feb items; December 2025 speech sweep; OSC conditional-loan lead (war.gov releases since Aug 2026); other DOE DPA/SPARK grid awards since Aug 2026 for listed utilities.

## Scout notes (2026-10-25 ~09:30 UTC, daily data-only run)
- **Added 1 mention:** `VOW3.DE` (Trump, Audi first U.S. plant, Perry GA rally ~8:09 PM ET Sat Oct 24; day 0 Mon Oct 26). Source is the Rapid Response 47 clip; the WANF-TV interview transcript is the archive link. Foreign tickers get no sectors/committee mapping (same as PIRC.MI/6690.HK).
- The Oct 24 pending note said "Michigan rally"; the Oct 24 rally was actually in Perry, Georgia (Michigan was only an early-voting post).
- **Exclusions:** Palm Beach gaggle (Musk/Ukraine, Alaska gas, Hormuz), WANF data-center comments, rally clips, Truth Social endorsements; admin X posts (Duffy highways, Rollins water treaty, Burgum, Wright, DOE, Hegseth).
- **Pending:** swap the VW source to the Roll Call/Trump Archive Perry rally transcript once posted and scan the full rally for other company names; VOW3.DE scores next run; MRK/BA/WMB/AAPL/BETA/RTX re-check after their +7d windows (Oct 26–29) and when filings close; IPI/ASIX/AEP re-check after +7d; Trump's September OGE 278-T; Vance Feb items; December 2025 speech sweep; OSC conditional-loan lead; other DOE DPA/SPARK grid awards for listed utilities.

## Scout notes (2026-10-26 ~09:15 UTC, daily data-only run)
- **Zero new mentions.** Checked Oct 25–26 Truth Social (Trump Archive day pages), the full Perry GA rally (abfbbef1), Oct 25 Port Huron MI rally (37375f84), Kudlow (cb52004e) and WJBK (d600ba77) interviews, two gaggles, X posts from family/cabinet/WH/RR47, X news. Exclusions: 3 entries (Oct 25 remarks; Oct 25–26 Truth Social incl. Fox News and HBO/Maher media complaints; admin/family X incl. Duffy BETA repeat of Oct 21).
- **Lead resolved:** VOW3.DE source swapped to the Roll Call Factbase Perry transcript (archive_url = Trump Archive item abfbbef1); quote now uses the transcript wording ($4.2B).
- **Congress +4:** Quiver re-check of all mentions since Sep 10 (/tmp/qcheck2.py) found Cleo Fields' PTR filed Oct 22 (House Clerk 20035669): 3× NVDA purchases Oct 1 (separate accounts) for the Sep 29 NVDA mention, TSM purchase Oct 9 for the Oct 14 TSM mention. House Clerk 2026FD.zip index + ptr-pdfs URLs work for verification.
- Ran /tmp/run_update_complete.py (Xetra open, partial Oct 26 bars dropped); publish guard run without re-running plain update.py.
- **Pending:** VOW3.DE scores next run (day 0 Oct 26); MRK/BA/WMB +7d windows close Oct 27, AAPL/BETA Oct 28–29, RTX/IPI/ASIX/AEP after; re-run the Quiver sweep then; Trump's September OGE 278-T; Vance Feb items; December 2025 speech sweep; OSC conditional-loan lead; DOE DPA/SPARK grid awards for listed utilities. Trump rallies this week: Corinth MS (Oct 26), Corpus Christi and Lubbock TX (Oct 27), Chillicothe OH (Oct 28), Daytona FL (Oct 30), Dubuque IA (Nov 1).


## Scout notes (2026-10-27 ~09:10 UTC, daily data-only run)
- **Added 2 mentions:** `CAKE` (Admin, Treasury Sec. Bessent, Cheesecake Factory lunch remarks + X post, ~2:57 PM ET Oct 26, Product endorsement; Trump's "very successful company" rally line is in the note; new `who` "Scott Bessent (Treasury Sec.)"; CAKE Q3 earnings Oct 27 confound) and `DK` (Admin, Vance Tyler TX rally Oct 13, DPA refinery expansion, missed then; surfaced by Vance's Oct 26 Topeka line; new `who` "JD Vance (Vice President)"). DK mapped XLE + Energy/Armed Services committees; CAKE XLY, no committees (like AEO).
- **Exclusions (4):** Corinth MS rally/gaggles/WLBT (Toyota Blue Springs $125M = Nov 2025 package, repeat), Vance Topeka/Belgrade (Bombardier repeat, USDA MPPEP $57.4M to unnamed independent processors), Truth Social posts (nurses initiative, endorsements), admin X posts (Wright BWXT and Rollins ADM site visits, WH Mississippi graphic, OSC loan to private Stoke Space).
- **Leads:** Quiver sweep (/tmp/qcheck2.py) found no new trades; VOW3.DE scored (day 0 Oct 26). Ran /tmp/run_update_complete.py again (Xetra open).
- **Pending:** CAKE/VOW3.DE +1d next run; AAPL/BETA +7d windows close Oct 28–29, RTX/IPI/ASIX/AEP after; re-run the Quiver sweep then; check other Vance/admin rally announcements since Sep for missed deals (the DK miss suggests Vance rally transcripts weren't scanned every day); Trump's September OGE 278-T; Vance Feb items; December 2025 speech sweep; DOE DPA/SPARK grid awards. Trump rallies this week: Corpus Christi and Lubbock TX (Oct 27), Chillicothe OH (Oct 28), Daytona FL (Oct 30), Dubuque IA (Nov 1).

## Scout notes (2026-10-28 ~09:15 UTC, daily data-only run)
- **Added 3 mentions:** `CEG` (Admin, DOE/Wright $5B conditional uprate loan, ~12:00 PM ET Oct 27, day 0 Oct 27, scored), `TXN` and `BMY` (Trump, Corpus Christi rally investment roll-call ~4:24 PM ET Oct 27, after close, day 0 Oct 28, unscored). CEG mapped like AEP (XLU, energy committees), TXN like MU, BMY like MRK.
- **Timing source:** pool.pp.tools reports 9986-9994 (walked in 2:39 PM CDT, ended 3:55 PM CDT); report bodies use local time with the zone in the "Sent" line.
- **Exclusions (3):** Texas rallies/gaggles (Apple/Lilly/Toyota/Audi repeats, Saronic/Hamm/Cantor private, Venezuelan oil cargo, unnamed gas plants); Vance Howell + Truth Social posts; admin X (WH Cheesecake Factory repeat, Duffy RTX repeat, port grants).
- **Pending:** TXN/BMY/CAKE score next run; AAPL/BETA +7d windows close Oct 28-29, RTX/IPI/ASIX/AEP after, CEG/TXN/BMY by Nov 3-4; re-run /tmp/qcheck2.py; sweep Vance/admin rally transcripts since Sep for missed deals; Trump's September OGE 278-T; Vance Feb items; December 2025 speech sweep; other DOE loan/DPA awards to listed utilities. Trump rallies: Chillicothe OH (Oct 28), Rock Hill SC, Daytona FL (Oct 30), Dubuque IA (Nov 1).

## Scout notes (2026-10-29 ~09:20 UTC, daily data-only run)
- **Added 5 mentions:** `LNT` (Admin, DOE $5.1B Alliant loan close, 8-K 8:15 AM ET Oct 28, scored), `WMT` (Admin, new `who` "Brooke Rollins (Agriculture Sec.)", X 3:00 PM ET Oct 28, scored; 2 Congress sales Jackson/Sessions), `FSLR` (Admin, Lutnick at First Solar Gaffney, quote first public 5:46 PM ET, day 0 Oct 29), `PCAR` (Trump, Kenworth Chillicothe ~8:24 PM ET, day 0 Oct 29) and `9984.T` (Trump, SoftBank Pike County gas plants ~8:26 PM ET = 9:26 AM JST Oct 29, day 0 Tokyo Oct 29). LNT mapped like CEG; FSLR XLK + energy committees; WMT XLP, no committees (like CAKE); 9984.T foreign, no mapping. /tmp/qcheck2.py alias added for 9984.T (SFTBY/SFTBF).
- **Congress +5:** WMT Jackson (PTR 20035551) and Sessions (PTR 20035563); Sessions's same PTR also adds NVDA (Sep 29), TSLA (Oct 16) and AAPL (Oct 20) spouse sales on Oct 2. House Clerk 2026FD.zip index re-downloaded to /tmp/fd26n.
- **Backlog sweep done:** 23 Vance transcripts Sep 3 to Oct 27 re-read (/tmp/sweep); no further missed deals (Webco worker-owned, Saronic private, Lima Stellantis repeat, NC Helene funding). Still open: other officials' (Wright, Burgum, Duffy, Rollins, Lutnick) site visits since Sep for listed-company awards.
- **Timing source:** pool.pp.tools reports 10030/10032 (Trump spoke 7:29 to 8:58 PM ET in Chillicothe). Lutnick First Solar remark time unknown ("Wednesday afternoon"); used the 5:46 PM ET release as first public time.
- **Pending:** FSLR/PCAR/9984.T score next run (9984.T's Oct 29 bar is complete but run_update_complete drops today's bars); TXN/BMY now scored; AAPL/BETA/RTX/IPI/ASIX/AEP/CEG +7d windows closing, re-run /tmp/qcheck2.py; Trump's September OGE 278-T; Vance Feb items; December 2025 speech sweep. Trump schedule: Rock Hill SC (Oct 29), Daytona FL (Oct 30), Dubuque IA (Nov 1).
## Scout notes (2026-10-30 ~09:20 UTC, daily data-only run)
- **Added 1 mention:** `CENX` (Trump, Rock Hill SC rally, ~2:13 PM ET Oct 29, scored; quote from our faster-whisper transcription of RSBN full video YgLEwkkV5hc at 1:00:54, since the Factbase transcript wasn't posted; swap source to the Trump Archive transcript once posted and re-check the wording). Sectors: CENX XLB, no peer, no committees. Exclusions +2 (total 103).
- **Congress +1:** Hern TXN Oct 14 sale (PTR 20035710, filed Oct 28). House Clerk 2026FD index re-downloaded to /tmp/fd26o.
- **Scored this run:** FSLR, PCAR, 9984.T (prices to Oct 29 close via /tmp/run_update_complete.py).
- **Leads:** Lutnick + Navarro Jul 27 2026 Century Aluminum Mt. Holly ribbon-cutting ("America-first trade policies at work", Post and Courier) was never tracked: verify a primary (Commerce release/video) and time before adding as an Admin row. Vance Oct 29 Weatherford TX and Trump Oct 29 Rock Hill transcripts to re-read when posted. Trump schedule: Daytona FL (Oct 30), Dubuque IA (Nov 1). Still open: other officials' site visits since Sep; Trump's September OGE 278-T; December 2025 speech sweep.
## Scout notes (2026-10-31 ~09:10 UTC, daily data-only run)
- **Added 2 mentions:** `JNJ` (Trump, Daytona Beach rally ~8:36 PM ET Fri Oct 30, transcript clip 00:35:33, pool report 10098 stage 7:57 PM; day 0 Mon Nov 2, unscored; mapped like BMY: XLV/IHE, health committees) and `CENX` (Admin, Lutnick quote in Century's GlobeNewswire release 7:09 PM ET Jul 27, day 0 Jul 28, scored). Lead from Oct 30 resolved.
- **Source swap done:** CENX Oct 29 Trump row now cites the Trump Archive Rock Hill transcript (e55f5585, 01:03:03).
- **Exclusions +2 (total 105):** Daytona rally + WH Florida fact sheet (pool report 10088, 2:15 PM ET; Lupin fact-sheet-only, private names, Fannie/Freddie); other Oct 30 items (Hy-Vee, Product of USA, Binance, Palisades, Vance Weatherford).
- **Quiver:** /tmp/qcheck2.py found no new trades. JNJ: latest Doggett Sep 8 purchase, outside window.
- **Pending:** JNJ scores after Mon Nov 2 close; re-check JNJ Quiver after Nov 9 and when filings close; Trump rallies Dubuque IA and Kansas (Sun Nov 1), Halloween tele-rallies Oct 31; Election Day Nov 3. Still open: other officials' site visits since Sep; Trump's September OGE 278-T; December 2025 speech sweep.

## Scout notes (2026-11-01 ~09:10 UTC, daily data-only run)
- **Zero new mentions.** Checked Oct 31 Truth Social (Trump Archive day page, 122 items incl. ~60 endorsements, 11 media posts), the Mar-a-Lago Halloween gaggle (a3ac8b40; Jensen Huang personal praise) and six tele-rallies (Audi repeat, unnamed auto plants, NYSE-to-Texas recap), Benny Johnson interview clips (Musk/CNN; Cheesecake Factory topic not transcribed, CAKE already tracked), X posts from family/cabinet/WH/RR47/agencies (Duffy quote-post of USDOT Joby/BETA Florida cargo flights treated under the Hegseth quote-post rule), X news. Exclusions +2 (total 107).
- **Quiver:** /tmp/qcheck2.py found no new trades. Prices still to Oct 30 close (weekend).
- **Pending:** JNJ scores after Mon Nov 2 close; Dubuque IA and Salina KS rallies (Sun Nov 1) and Election-eve events (Nov 2) to read next run; re-check JNJ Quiver after Nov 9; optional: if the full Benny Johnson interview transcript appears, check the Cheesecake Factory wording. Still open: other officials' site visits since Sep; Trump's September OGE 278-T; December 2025 speech sweep.

## Scout notes (2026-11-02 ~09:15 UTC, daily data-only run)
- **Added 1 mention:** `DE` (Trump, Dubuque IA rally clip 00:54:43, pool report 10119 stage 3:35 PM CST, so ~5:30 PM ET Sun Nov 1; day 0 Mon Nov 2, unscored; DE already mapped in sectors/committees). Quiver: no DE trades in window (latest Newhouse Jul 10).
- **Exclusions +2 (total 109):** Nov 1 rallies/gaggle/interview (Salina Merck/Bombardier/Boeing exact repeats of Oct 19; Dubuque Cheesecake Factory "good company" treated as a repeat inside the Oct 26 CAKE window; Mesabi Metallics steel mill private/Essar); Nov 1 Truth Social endorsements + admin/family X.
- **Quiver:** /tmp/qcheck2.py found no new trades. Prices still to Oct 30 close (ran before Monday's open).
- **Pending:** JNJ and DE score after Mon Nov 2 close; Nov 2 Lincoln Memorial remarks (2 PM ET) and Election-eve tele-rallies to read next run; Election Day Nov 3; re-check JNJ/DE Quiver after Nov 9. Still open: other officials' site visits since Sep; Trump's September OGE 278-T; December 2025 speech sweep.

## Scout notes (2026-11-04 ~09:10 UTC, daily data-only run)
- **Zero new mentions.** Checked Nov 3–early Nov 4 Truth Social (endorsements, election commentary, Fox News/Fox Corp. media criticism), Bongino Election Day interview (Lilly/Merck/Pfizer general drugmaker roll-call), Burgum/Rollins/Mullin stakeouts (no listed company), WH manufacturing-renaissance fact sheet (Audi/Apple/Bombardier already tracked; Westinghouse private; Carrier fact-sheet-only after Carrier's Oct 22 release), Rapid Response 47 Bongino clips, cabinet/family/WH X. **Texas tele-rally transcripts (Nov 2 6:15/7:00 PM ET) still not on Factbase.** Exclusions +2 (total 113).
- **Quiver:** /tmp/qcheck2.py found no new trades (all windows HAVE). Prices to Nov 3 close via /tmp/run_update_complete.py. Stats: day-0 55.6%, 30d 45.3% (was 46.6%), portfolio −3.4% vs S&P +7.6%.
- **Pending:** Texas tele-rally transcripts when posted; re-check JNJ/DE Quiver after Nov 9; other officials' site visits since Sep; Trump's September OGE 278-T; December 2025 speech sweep. Optional lead only: Oklo/T1 Energy appear in secondary coverage of a manufacturing report — verify a primary speaker praise before adding.

## Scout notes (2026-11-05 ~09:15 UTC, daily data-only run)
- **Added 1 mention:** `AMZN` (Admin, Brooke Rollins X thank-you for Amazon's $25 Thanksgiving meal, 7:37 AM ET Nov 3, scored +1.7 vs S&P; Amazon announced Nov 2). Mapped XLY + FDN peer, no committees (like WMT/CAKE). Congress +2: Sessions AMZN Oct 27 sale (PTR 20035563) and Capito AAPL Oct 21 partial sale (filed Nov 4, linked to Don Jr Oct 20). Exclusions +2 (total 115).
- **Texas tele-rallies:** still no Trump Archive / Factbase item for the Nov 2 6:15/7:00 PM ET Texas calls (other Nov 2 teles already read on Nov 3–4).
- **Quiver:** /tmp/qcheck2.py found Capito AAPL NEW; JNJ/DE +7d windows still open through ~Nov 9. Senate efdsearch blocked to curl this run — Capito row cites Quiver only.
- **Pending:** Texas tele-rally transcripts when posted; re-check JNJ/DE Quiver after Nov 9; other officials' site visits since Sep; Trump's September OGE 278-T; December 2025 speech sweep. Optional Oklo/T1 Energy only if a primary speaker praise appears (still secondary manufacturing-report coverage only).
