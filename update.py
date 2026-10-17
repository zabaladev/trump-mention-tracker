#!/usr/bin/env python3
"""Re-fetch prices (Yahoo Finance via yfinance) and regenerate index.html + data.json.
Usage: pip install yfinance pandas && python update.py"""
import json, os, datetime as dt, statistics as st
import pandas as pd, yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(f'{HERE}/mentions.json'))
EX = json.load(open(f'{HERE}/exclusions.json'))
DISC = json.load(open(f'{HERE}/disclosures.json'))
DNOTES = [
 'Sources are public only: OGE Form 278e/278-T (via OGE, whitehouse.gov, and reporting by CNN, WSJ, CNBC), SEC 13D/13G/8-K/S-3 filings, company disclosures, and the family members\' own posts.',
 'Amounts are disclosed as ranges, not exact figures. Reports can be filed up to 45 days after a trade (some were later), so overlaps were often not public at the time of the comment.',
 "Trump's accounts are discretionary and managed by third parties. The White House says he plays no role in trades, and they made 21,000+ trades in 2025, so overlap with any single post is expected by chance.",
 'Not checked systematically: congressional STOCK Act trades. Only MP Materials was checked (Benzinga congressional-trades page shows one trade, May 2022, outside any window). Capitol Trades / Quiver / House & Senate sites were not scraped for every ticker.',
 'Not checked: OGE reports for Bessent, Lutnick (said he may not own stocks), Navarro, and other officials for every mentioned asset. No public holdings found for Ivanka/Kushner (Affinity Partners) or Lara Trump in tracked assets.',
 'These are factual timing overlaps and holdings. They are not evidence of wrongdoing, coordination or insider trading, and none is alleged.']
TODAY = pd.Timestamp(dt.date.today())
# pre windows END at the last close BEFORE the entry day (pure pre-mention);
# 'day0' = prior close -> entry-day close (mention-day reaction); post windows start at entry close.
HOR = ['-30d', '-7d', 'day0', '+1d', '+7d', '+30d', '+90d', 'to date']
BENCH = {'sp': 'SPY', 'dow': 'DIA', 'btc': 'BTC-USD'}

tick = {m['ticker'] for m in M if m.get('ticker') and not m['ticker'].startswith('BASKET:')}
for m in M:
    for t, _ in m.get('basket', []): tick.add(t)
tick |= set(BENCH.values())
px = {}
for t in sorted(tick):
    try:
        d = yf.download(t, start='2020-05-01', progress=False, auto_adjust=True)
        s = d['Close'].squeeze().dropna() if len(d) else pd.Series(dtype=float)
        if len(s):
            s.index = pd.to_datetime(s.index).tz_localize(None).normalize(); px[t] = s[~s.index.duplicated()]
    except Exception as e:
        print('fail', t, e)

def asof(s, d):
    s2 = s[s.index <= d]; return s2.iloc[-1] if len(s2) else None

def basket_series(m):
    comps = [px[t] for t, _ in m['basket'] if t in px]
    if not comps: return None
    d0 = pd.Timestamp(m['date'])
    idx = sorted(set().union(*[c.index for c in comps]))
    idx = pd.DatetimeIndex(idx)
    norm = []
    for c in comps:
        c2 = c.reindex(idx).ffill()
        b = c2[c2.index >= d0].dropna()
        if not len(b): continue
        norm.append(c2 / b.iloc[0])
    return pd.concat(norm, axis=1).mean(axis=1, skipna=True).dropna() if norm else None

def windows(s, d):
    """dict horizon -> (start_date, end_date) using trading dates of s. d = mention date."""
    after = s.index[s.index >= d]
    if not len(after): return None, {}
    e = after[0]; i = s.index.get_loc(e); W = {}
    prev = s.index[i-1] if i > 0 else None
    if prev is not None:
        W['day0'] = (prev, e)
        for k, n in (('-30d', 30), ('-7d', 7)):
            st_ = s.index[s.index <= e - pd.Timedelta(days=n)]
            if len(st_) and st_[-1] < prev: W[k] = (st_[-1], prev)
    if i + 1 < len(s): W['+1d'] = (e, s.index[i+1])
    for k, n in (('+7d', 7), ('+30d', 30), ('+90d', 90)):
        tg = e + pd.Timedelta(days=n)
        if tg <= s.index[-1]: W[k] = (e, s.index[s.index >= tg][0])
    W['to date'] = (e, s.index[-1])
    return e, W

def ret(s, a, b):
    va, vb = asof(s, a), asof(s, b)
    return None if va is None or vb is None else float(vb / va - 1)

rows = []
for m in M:
    r = dict(m); r.update(returns={}, ex_sp={}, ex_dow={}, ex_btc={})
    t = m.get('ticker')
    if t and t.startswith('BASKET:'):
        s = basket_series(m)
        if s is not None: px[t] = s
    s = px.get(t) if t else None
    if s is None:
        r['status'] = m.get('note') or 'no price data'; rows.append(r); continue
    e, W = windows(s, pd.Timestamp(m['date']))
    if e is None: r['status'] = 'no price after date'; rows.append(r); continue
    r.update(status='ok', entry_date=str(e.date()), entry_price=float(s.loc[e]))
    for k, (a, b) in W.items():
        v = ret(s, a, b); r['returns'][k] = v
        for key, bt in BENCH.items():
            if key == 'btc' and m['type'] != 'crypto': continue
            bv = ret(px[bt], a, b)
            if bv is not None: r['ex_' + key][k] = v - bv
    if m.get('basket'):
        comp = []
        for ct, name in m['basket']:
            cs = px.get(ct)
            if cs is None: comp.append(dict(ticker=ct, name=name, returns={}, ex_sp={}, ex_dow={})); continue
            cr = dict(ticker=ct, name=name, returns={}, ex_sp={}, ex_dow={})
            for k, (a, b) in W.items():
                v = ret(cs, a, b)
                if v is None: continue
                cr['returns'][k] = v
                for key in ('sp', 'dow'):
                    bv = ret(px[BENCH[key]], a, b)
                    if bv is not None: cr['ex_' + key][k] = v - bv
            comp.append(cr)
        r['components'] = comp
    rows.append(r)
for r in rows:
    r['disclosures'] = [d for d in DISC if [r['date'], r.get('ticker')] in d['applies']]
ok = [r for r in rows if r['status'] == 'ok']

# portfolios ($1,000 at entry close per priced mention) vs same cash flows into SPY and DIA
start = min(pd.Timestamp(r['entry_date']) for r in ok)
days = pd.date_range(start, TODAY, freq='D')
ff = {t: s.reindex(days.union(s.index)).ffill().reindex(days) for t, s in px.items()}
def curve(sel, hold=None):
    out = {k: pd.Series(0.0, index=days) for k in ('val', 'sp', 'dow', 'inv')}
    for r in sel:
        d0 = pd.Timestamp(r['entry_date']); mask = days >= d0
        for key, ser in (('val', ff[r['ticker']]), ('sp', ff['SPY']), ('dow', ff['DIA'])):
            p0 = asof(px[r['ticker']] if key == 'val' else px[BENCH[key]], d0)
            a = ser * (1000 / p0)
            if hold:
                ex = d0 + pd.Timedelta(days=hold); a = a.where(days <= ex, a[days <= ex].iloc[-1])
            out[key][mask] += a[mask].fillna(0)
        out['inv'][mask] += 1000
    return out
def pack(c):
    step = 3
    return {k: [round(x, 1) for x in v[::step]] for k, v in c.items()} | {'dates': [str(d.date()) for d in days[::step]],
            'final': {k: float(v.iloc[-1]) for k, v in c.items()}}
port = {'hold': pack(curve(ok)), 'hold30': pack(curve(ok, 30))}
# per-group portfolio finals for report
gport = {}
for g in ('Trump', 'Family', 'Admin'):
    sel = [r for r in ok if r['group'] == g]
    if sel: gport[g] = {k: float(v.iloc[-1]) for k, v in curve(sel).items()}

grid = days[::3]
for r in ok:
    a = ff[r['ticker']].reindex(grid) / r['entry_price']
    e0 = pd.Timestamp(r['entry_date']); r['sp0'] = float(asof(px['SPY'], e0)); r['dia0'] = float(asof(px['DIA'], e0))
    r['curve'] = [None if (d < pd.Timestamp(r['entry_date']) or pd.isna(v)) else round(float(v), 4) for d, v in zip(grid, a)]
gridd = dict(dates=[str(d.date()) for d in grid], SPY=[round(float(x), 3) for x in ff['SPY'].reindex(grid)],
             DIA=[round(float(x), 3) for x in ff['DIA'].reindex(grid)])
data = dict(grid=gridd, generated=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), horizons=HOR,
            rows=rows, exclusions=EX, disclosure_notes=DNOTES, portfolio=port, group_portfolio=gport)
json.dump(data, open(f'{HERE}/data.json', 'w'), indent=1, default=float)
html = open(f'{HERE}/template.html').read()
html = html.replace('/*__DATA__*/null', json.dumps(data, default=float)).replace('/*__CHARTJS__*/', open(f'{HERE}/chart.umd.min.js').read())
open(f'{HERE}/index.html', 'w').write(html)
print('mentions', len(rows), 'priced', len(ok))
