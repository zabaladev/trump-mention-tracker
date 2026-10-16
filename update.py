#!/usr/bin/env python3
"""Re-fetch prices (Yahoo Finance via yfinance) and regenerate index.html.
Usage: pip install yfinance pandas && python update.py"""
import json, datetime as dt, statistics as st
import pandas as pd, yfinance as yf

HERE = __file__.rsplit('/', 1)[0] if '/' in __file__ else '.'
M = json.load(open(f'{HERE}/mentions.json'))
TODAY = pd.Timestamp(dt.date.today())
HOR = {'-7d': -7, '-1d': -1, '+1d': 1, '+7d': 7, '+30d': 30, '+90d': 90}

tickers = sorted({m['ticker'] for m in M if m['ticker']} | {'SPY', 'BTC-USD'})
px = {}
for t in tickers:
    try:
        d = yf.download(t, start='2020-06-01', progress=False, auto_adjust=True)
        s = d['Close'].squeeze().dropna() if len(d) else pd.Series(dtype=float)
        if len(s): s.index = pd.to_datetime(s.index).tz_localize(None).normalize(); px[t] = s
    except Exception as e:
        print('fail', t, e)

def at_or_after(s, d):
    s2 = s[s.index >= d]; return (s2.index[0], s2.iloc[0]) if len(s2) else (None, None)
def at_or_before(s, d):
    s2 = s[s.index <= d]; return (s2.index[-1], s2.iloc[-1]) if len(s2) else (None, None)

def window(s, base_d, h):
    """return (start_value, end_value) for horizon h relative to base date (trading-row based for +-1d)."""
    i = s.index.get_loc(base_d)
    if h == -1: return (s.iloc[i-1], s.iloc[i]) if i > 0 else None
    if h == 1: return (s.iloc[i], s.iloc[i+1]) if i+1 < len(s) else None
    if h < 0:
        d, v = at_or_before(s, base_d + pd.Timedelta(days=h))
        return (v, s.iloc[i]) if d is not None and d < base_d else None
    target = base_d + pd.Timedelta(days=h)
    if target > s.index[-1]: return None
    d, v = at_or_after(s, target); return (s.iloc[i], v)

def bench_ret(b, d0, d1):
    _, v0 = at_or_before(b, d0); _, v1 = at_or_before(b, d1)
    return None if v0 is None or v1 is None else v1 / v0 - 1

rows = []
for m in M:
    r = dict(m); r['returns'] = {}; r['excess'] = {}
    t = m['ticker']; s = px.get(t)
    if s is None:
        r['status'] = m.get('note') or 'no price data'; rows.append(r); continue
    bd, bv = at_or_after(s, pd.Timestamp(m['date']))
    if bd is None: r['status'] = 'no price after date'; rows.append(r); continue
    bench = 'BTC-USD' if m['type'] == 'crypto' else 'SPY'; b = px[bench]
    r.update(benchmark=bench, entry_date=str(bd.date()), entry_price=float(bv), status='ok')
    i = s.index.get_loc(bd)
    for k, h in list(HOR.items()) + [('to date', None)]:
        if h is None: w = (bv, s.iloc[-1]); d0, d1 = bd, s.index[-1]
        else:
            w = window(s, bd, h)
            if w is None: continue
            if h == -1: d0, d1 = s.index[i-1], bd
            elif h == 1: d0, d1 = bd, s.index[i+1]
            elif h < 0: d0, d1 = bd + pd.Timedelta(days=h), bd
            else: d0, d1 = bd, at_or_after(s, bd + pd.Timedelta(days=h))[0]
        ret = float(w[1] / w[0] - 1); r['returns'][k] = ret
        br = bench_ret(b, d0, d1)
        if br is not None: r['excess'][k] = ret - br
    rows.append(r)

ok = [r for r in rows if r['status'] == 'ok']
def summarize(group):
    out = {}
    for k in list(HOR) + ['to date']:
        v = [r['returns'][k] for r in group if k in r['returns']]
        e = [r['excess'][k] for r in group if k in r['excess']]
        if not v: continue
        out[k] = dict(n=len(v), win=sum(x > 0 for x in v) / len(v), beat=(sum(x > 0 for x in e) / len(e)) if e else None,
                      mean=st.mean(v), median=st.median(v), mean_excess=st.mean(e) if e else None)
    return out
stats = {'all': summarize(ok)}
for key in ['who', 'type', 'category']:
    for g in sorted({r[key] for r in ok}):
        stats[f'{key}: {g}'] = summarize([r for r in ok if r[key] == g])

# pre-mention run-up signal
runup = [r for r in ok if '-7d' in r['excess']]
pre_pos = [r for r in runup if r['excess']['-7d'] > 0]
signal = dict(n=len(runup), share_outperform_pre7=len(pre_pos)/len(runup) if runup else None,
              mean_excess_pre7=st.mean([r['excess']['-7d'] for r in runup]) if runup else None,
              mean_excess_pre1=st.mean([r['excess']['-1d'] for r in ok if '-1d' in r['excess']]))

# portfolios
start = min(pd.Timestamp(r['entry_date']) for r in ok)
days = pd.date_range(start, TODAY, freq='D')
ff = {t: s.reindex(days.union(s.index)).ffill().reindex(days) for t, s in px.items()}
def portfolio(hold=None):
    val = pd.Series(0.0, index=days); spy = pd.Series(0.0, index=days); inv = pd.Series(0.0, index=days)
    for r in ok:
        d0 = pd.Timestamp(r['entry_date']); s = ff[r['ticker']]; b = ff['SPY']
        b0 = b.loc[d0] if not pd.isna(b.loc[d0]) else b[b.index <= d0].dropna().iloc[-1]
        units = 1000 / r['entry_price']; bunits = 1000 / b0
        mask = days >= d0
        a = s * units; bb = b * bunits
        if hold:
            exit_d = d0 + pd.Timedelta(days=hold)
            a = a.where(days <= exit_d, a[days <= exit_d].iloc[-1]); bb = bb.where(days <= exit_d, bb[days <= exit_d].iloc[-1])
        val[mask] += a[mask]; spy[mask] += bb[mask]; inv[mask] += 1000
    return dict(dates=[str(d.date()) for d in days[::3]], value=[round(x, 2) for x in val[::3]],
                spy=[round(x, 2) for x in spy[::3]], invested=[round(x, 2) for x in inv[::3]],
                final_value=float(val.iloc[-1]), final_spy=float(spy.iloc[-1]), invested_total=float(inv.iloc[-1]))
port = {'hold': portfolio(), 'hold30': portfolio(30)}

data = dict(generated=str(dt.datetime.now(dt.timezone.utc))[:16] + ' UTC', rows=rows, stats=stats, signal=signal, portfolio=port)
json.dump(data, open(f'{HERE}/data.json', 'w'), indent=1, default=float)
html = open(f'{HERE}/template.html').read().replace('/*__DATA__*/null', json.dumps(data, default=float)).replace('/*__CHARTJS__*/', open(f'{HERE}/chart.umd.min.js').read())
open(f'{HERE}/index.html', 'w').write(html)
print('mentions', len(rows), 'priced', len(ok))
