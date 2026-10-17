#!/usr/bin/env python3
"""Peer-outperformance ranking of members of Congress from their disclosed stock trades.

Inputs (public data): per-member trade lists from Quiver Quantitative's public politician pages
(which compile House Clerk and Senate eFD periodic transaction reports), cached as JSON in
../congress/memv/ and ../congress/memraw/<bioguide>.json by ../congress/qmem.py and qraw.py, plus the congress-legislators dataset
(../congress/leg.json). Prices: Yahoo Finance via yfinance (adjusted closes).

Each trade is scored as: sign * (stock total return - SPY total return) from the close on the
trade date to H calendar days later (H = 30, 90). sign = +1 for purchases, -1 for sales.
Members need >= 10 scored trades on >= 8 different trade dates.
Per member: mean score, 95% range from a bootstrap that resamples whole trade dates, hit rate,
dollar-weighted mean (range midpoints), mean minus chamber average ("vs peers"), and a
Benjamini-Hochberg q-value across all members ranked. Output: rankings.json (public).
No allegations: this is a statistical description of public filings.
"""
import json, os, glob, datetime as dt, numpy as np, pandas as pd, yfinance as yf
import re as _re
def _amt(r):
    """Range midpoint in $; falls back to parsing the disclosed range text."""
    v = r[14] if len(r) > 14 else None
    try:
        f = float(v)
        if f == f and f > 0: return f
    except (TypeError, ValueError): pass
    nums = [float(x.replace(',', '')) for x in _re.findall(r'[\d,]+', str(r[10] if len(r) > 10 else '')) if x.replace(',', '')]
    return sum(nums[:2]) / len(nums[:2]) if nums else 0.0


HERE = os.path.dirname(os.path.abspath(__file__)); CG = os.path.join(HERE, '..', 'congress')
START = '2023-01-01'; HS = (30, 90); B = 4000; MINN = 10; MIND = 8; rng = np.random.default_rng(7)
TODAY = pd.Timestamp(dt.date.today())
leg = {m['id']['bioguide']: m for m in json.load(open(f'{CG}/leg.json'))}
rows = []
for f in glob.glob(f'{CG}/memv/*.json'):
    b = os.path.basename(f)[:-5]
    if b not in leg: continue
    fr = f'{CG}/memraw/{b}.json'   # full page data (incl. older filings) when available
    try: d = json.load(open(fr))['rows'] if os.path.exists(fr) else json.load(open(f))
    except Exception: continue
    ln = leg[b]['name']['last'].lower()
    for r in d:
        # keep only this member's rows (the page id carries the bioguide; older filings carry the name only)
        if not ((r[7] and b in r[7]) or ln in (r[6] or '').lower()): continue
        tk, ty, tr = r[0], r[1] or '', (r[3] or '')[:10]
        if not tk or r[9] not in ('Stock', None, '-') or not tr[:4].isdigit() or tr < START: continue
        sg = 1 if ty.startswith('Purchase') else -1 if ty.startswith('Sale') else 0
        if not sg: continue
        rows.append(dict(b=b, tk=tk.replace('.', '-').upper().strip(), d=tr, s=sg, amt=_amt(r), ch=r[11] if len(r) > 11 else None, rid=r[7] or f'{b}-{tr}-{tk}-{len(rows)}'))
df = pd.DataFrame(rows).drop_duplicates('rid')
print('trades', len(df), 'members', df.b.nunique(), 'tickers', df.tk.nunique())
tks = sorted(set(df.tk)) + ['SPY']
import pickle, time
CACHE = f'{CG}/pxcache.pkl'   # local price cache (not published) so reruns don't hammer Yahoo
px = pickle.load(open(CACHE, 'rb')) if os.path.exists(CACHE) else {}
if 'SPY' in px and px['SPY'].index[-1] < TODAY - pd.Timedelta(days=4): px = {}   # stale cache: refetch everything
bad = set(px.pop('_bad', set()))   # tickers Yahoo had no prices for (delisted etc.)
miss = [t for t in tks if t not in px and t not in bad]
for i in range(0, len(miss), 80):
    chunk = miss[i:i + 80]
    for attempt in range(4):
        try:
            z = yf.download(chunk, start='2022-12-15', progress=False, auto_adjust=True, threads=False)['Close']
        except Exception as e:
            print('dl fail', e); z = None
        if isinstance(z, pd.Series): z = z.to_frame(chunk[0])
        got = 0 if z is None else sum(1 for c in z.columns if z[c].notna().sum() > 20)
        if z is not None and (got or attempt == 1): break   # an all-empty chunk is usually all delisted
        print('retry after pause', i, attempt); time.sleep(60 * (attempt + 1))
    if z is not None:
        for c in z.columns:
            s_ = z[c].dropna()
            if len(s_) > 20: s_.index = pd.to_datetime(s_.index).tz_localize(None).normalize(); px[c] = s_
            else: bad.add(c)
        bad.update(t for t in chunk if t not in px)
    pickle.dump({**px, '_bad': bad}, open(CACHE, 'wb')); time.sleep(4)
print('priced tickers', len(px))
spy = px['SPY']; last = spy.index[-1]
def at(s, t):  # close on t or the next trading day
    i = s.index.searchsorted(t); return (s.index[i], s.iloc[i]) if i < len(s) else (None, None)
def asof(s, t):
    i = s.index.searchsorted(t, side='right') - 1; return s.iloc[i] if i >= 0 else None
for H in HS:
    sc = []
    for r in df.itertuples():
        s = px.get(r.tk); t0 = pd.Timestamp(r.d); t1 = t0 + pd.Timedelta(days=H)
        if s is None or t1 > last or s.index[0] > t0 or s.index[-1] < t1: sc.append(np.nan); continue
        e0, p0 = at(s, t0)
        if e0 is None or (e0 - t0).days > 5: sc.append(np.nan); continue
        p1 = asof(s, t1); q0 = asof(spy, e0); q1 = asof(spy, t1)
        x = (p1 / p0 - 1) - (q1 / q0 - 1)
        sc.append(np.nan if abs(x) > 3 else r.s * x)        # drop obviously broken price series (>300%)
    df[f'x{H}'] = sc
def boot(x, g):
    """Cluster bootstrap of the mean, resampling trade dates."""
    u, inv = np.unique(g, return_inverse=True); K = len(u)
    cs = np.bincount(inv, weights=x, minlength=K); cn = np.bincount(inv, minlength=K)
    idx = rng.integers(0, K, size=(B, K)); m = cs[idx].sum(1) / cn[idx].sum(1)
    lo, hi = np.percentile(m, [2.5, 97.5]); p = 2 * min((m <= 0).mean(), (m >= 0).mean())
    return float(lo), float(hi), max(float(p), 1 / B)
cm = {k: {} for k in ('All', 'House', 'Senate')}
for H in HS:
    v = df.dropna(subset=[f'x{H}'])
    cm['All'][str(H)] = float(v[f'x{H}'].mean())
    for c in ('House', 'Senate'): cm[c][str(H)] = float(v[v.ch == c][f'x{H}'].mean()) if (v.ch == c).any() else None
mem = []
for b, g in df.groupby('b'):
    m = leg[b]; term = m['terms'][-1]; ch = 'Senate' if term['type'] == 'sen' else 'House'
    nm = m['name'].get('official_full') or (m['name']['first'] + ' ' + m['name']['last'])
    o = dict(name=nm, bioguide=b, chamber=ch, party=(term.get('party') or '?')[:1], state=term.get('state', ''),
             src=f"https://www.quiverquant.com/congresstrading/politician/{nm.replace(' ', '%20')}-{b}",
             trades=int(len(g)), n={}, mean={}, ci={}, hit={}, wmean={}, peer={}, p={}, q={})
    for H in HS:
        k = str(H); v = g.dropna(subset=[f'x{H}']); x = v[f'x{H}'].values; o['n'][k] = int(len(x))
        o.setdefault('dates', {})[k] = int(v.d.nunique())
        if len(x) < MINN or v.d.nunique() < MIND:
            o['mean'][k] = None; o['ci'][k] = [None, None]; o['hit'][k] = None; o['wmean'][k] = None; o['peer'][k] = None; o['p'][k] = None; continue
        lo, hi, p = boot(x, v.d.values); w = v.amt.values.astype(float)
        o['mean'][k] = float(x.mean()); o['ci'][k] = [lo, hi]; o['hit'][k] = float((x > 0).mean())
        o['wmean'][k] = float((x * w).sum() / w.sum()) if w.sum() > 0 else None
        o['peer'][k] = float(x.mean() - (cm[ch][k] or 0)); o['p'][k] = p
    if any(o['mean'][str(H)] is not None for H in HS): mem.append(o)
for H in HS:  # Benjamini-Hochberg across ranked members
    k = str(H); L = sorted([o for o in mem if o['p'][k] is not None], key=lambda o: o['p'][k]); n = len(L); prev = 1.0
    for i in range(n - 1, -1, -1):
        prev = min(prev, L[i]['p'][k] * n / (i + 1)); L[i]['q'][k] = prev
    for o in mem: o['q'].setdefault(k, None)
for o in mem:
    for dct in ('mean', 'wmean', 'peer', 'p', 'q', 'hit'):
        o[dct] = {k: (None if v is None else round(v, 5)) for k, v in o[dct].items()}
    o['ci'] = {k: [None if a is None else round(a, 5) for a in v] for k, v in o['ci'].items()}
out = dict(generated=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), from_=START, to=str(df.d.max()), prices_to=str(last.date()),
           n_trades=int(len(df)), n_scored={str(H): int(df[f'x{H}'].notna().sum()) for H in HS}, n_members_with_trades=int(df.b.nunique()),
           min_trades=MINN, min_dates=MIND, chamber_mean=cm, members=mem,
           source_note='Quiver Quantitative public per-member pages (compiled from House Clerk and Senate eFD periodic transaction reports); current members only; prices from Yahoo Finance.')
out['from'] = out.pop('from_')
json.dump(out, open(f'{HERE}/rankings.json', 'w'), separators=(',', ':'))
print('ranked', len(mem), {str(H): sum(1 for o in mem if o['mean'][str(H)] is not None) for H in HS})
