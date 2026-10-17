#!/usr/bin/env python3
"""Re-fetch prices (Yahoo Finance via yfinance) and regenerate index.html + data.json.
Usage: pip install yfinance pandas && python update.py"""
import json, os, datetime as dt, statistics as st
import numpy as np
import pandas as pd, yfinance as yf

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(f'{HERE}/mentions.json'))

# Post time from the post's own ID (#12g): Truth Social (Mastodon) IDs carry the creation time in ms (id >> 16);
# X IDs are Twitter snowflakes ((id >> 22) + 1288834974657 ms). Gives an exact ET timestamp for linked posts,
# and auto-flags weekday posts at/after 4 PM ET as after_close (stocks/funds only; crypto trades 24/7).
def _post_time(src):
    import re as _re, datetime as _dt
    from zoneinfo import ZoneInfo
    m = _re.search(r'truthsocial\.com/@\w+/(?:posts/)?(\d{15,})', src or '')
    if m: ms, k = int(m.group(1)) >> 16, 'Truth Social post ID'
    else:
        m = _re.search(r'(?:x|twitter)\.com/\w+/status/(\d{15,})', src or '')
        if not m: return None
        ms, k = (int(m.group(1)) >> 22) + 1288834974657, 'X post ID'
    return _dt.datetime.fromtimestamp(ms / 1000, _dt.timezone.utc).astimezone(ZoneInfo('America/New_York')), k
for _m in M:
    _pt = _post_time(_m.get('source'))
    if not _pt: continue
    _t, _k = _pt
    _m.setdefault('time_et', _t.strftime('%Y-%m-%d %H:%M')); _m.setdefault('time_src', _k)
    if (_m['type'] != 'crypto' and _t.weekday() < 5 and _t.hour >= 16 and _t.strftime('%Y-%m-%d') == _m['date']
            and 'after_close' not in _m):
        _m['after_close'] = True; _m['after_close_auto'] = True
EX = json.load(open(f'{HERE}/exclusions.json'))
DISC = json.load(open(f'{HERE}/disclosures.json'))
CONG = json.load(open(f'{HERE}/congress.json'))
SEC = json.load(open(f'{HERE}/sectors.json'))  # ticker -> Yahoo sector -> SPDR sector ETF
FAM = json.load(open(f'{HERE}/family_cos.json'))  # family-linked listed cos + SEC milestones
DNOTES = [
 'Sources are public only: OGE Form 278e/278-T (via OGE, whitehouse.gov, and reporting by CNN, WSJ, CNBC), SEC 13D/13G/8-K/S-3 filings, company disclosures, and the family members\' own posts.',
 'Amounts are disclosed as ranges, not exact figures. Reports can be filed up to 45 days after a trade (some were later), so overlaps were often not public at the time of the comment.',
 "Trump's accounts are discretionary and managed by third parties. The White House says he plays no role in trades, and they made 21,000+ trades in 2025, so overlap with any single post is expected by chance.",
 'Congressional STOCK Act trades come from Quiver Quantitative\'s public per-ticker pages, which compile official House Clerk and Senate eFD filings. Every priced stock/ETF mention and sector-basket component was checked for trades from 30 days before to 7 days after the comment. Members must file within 30–45 days, so most trades weren\'t public at comment time. Not covered: crypto, futures, and members not in the current-legislators list (party/chamber shown as ? if unmatched). Quiver can miss or lag filings.',
 'Not checked: OGE reports for Bessent, Lutnick (said he may not own stocks), Navarro, and other officials for every mentioned asset. No public holdings found for Ivanka/Kushner (Affinity Partners) or Lara Trump in tracked assets.',
 'These are factual timing overlaps and holdings. They are not evidence of wrongdoing, coordination or insider trading, and none is alleged.']
TODAY = pd.Timestamp(dt.date.today())
# pre windows END at the last close BEFORE the entry day (pure pre-mention);
# 'day0' = prior close -> entry-day close (mention-day reaction); post windows start at entry close.
HOR = ['-30d', '-7d', 'day0', '+1d', '+7d', '+30d', '+90d', 'to date']
# Index benchmarks (price indices, plus dividend-reinvested ETF total-return proxies); ETF fallback if Yahoo lacks the index.
BENCHES = [('sp', '^GSPC', 'SPY', 'S&P 500'), ('dow', '^DJI', 'DIA', 'Dow Jones (DJIA)'), ('ixic', '^IXIC', 'ONEQ', 'Nasdaq Composite'),
           ('ndx', '^NDX', 'QQQ', 'Nasdaq 100'), ('rut', '^RUT', 'IWM', 'Russell 2000'), ('rui', '^RUI', 'IWB', 'Russell 1000'),
           ('rua', '^RUA', 'IWV', 'Russell 3000'), ('w5000', '^W5000', 'VTI', 'Wilshire 5000 (total market)'), ('mid', '^MID', 'MDY', 'S&P MidCap 400'),
           # Total-return proxies: ETF closes adjusted for dividends (auto_adjust), i.e. dividends reinvested, minus small ETF fees.
           ('sp_tr', 'SPY', 'SPY', 'S&P 500 total return (SPY)'), ('dow_tr', 'DIA', 'DIA', 'Dow total return (DIA)'),
           ('ndx_tr', 'QQQ', 'QQQ', 'Nasdaq 100 total return (QQQ)'), ('vti_tr', 'VTI', 'VTI', 'US total market total return (VTI)')]
BENCH = {'btc': 'BTC-USD'}

tick = {m['ticker'] for m in M if m.get('ticker') and not m['ticker'].startswith('BASKET:')}
for m in M:
    for t, _ in m.get('basket', []): tick.add(t)
tick |= {v['etf'] for v in SEC['tickers'].values()} | {v['peer'] for v in SEC['tickers'].values() if v.get('peer')}
tick |= set(BENCH.values()) | {b[1] for b in BENCHES} | {'SPY', 'DIA'} | {c['ticker'] for c in FAM['companies']}
px = {}
for t in sorted(tick):
    try:
        d = yf.download(t, start='2020-05-01', progress=False, auto_adjust=True)
        s = d['Close'].squeeze().dropna() if len(d) else pd.Series(dtype=float)
        if len(s):
            s.index = pd.to_datetime(s.index).tz_localize(None).normalize(); px[t] = s[~s.index.duplicated()]
    except Exception as e:
        print('fail', t, e)
BLABEL = {}
for k, idx, etf, lab in BENCHES:
    if idx in px and len(px[idx]) > 300: BENCH[k] = idx; BLABEL[k] = lab
    else:
        d = yf.download(etf, start='2020-05-01', progress=False, auto_adjust=True)['Close'].squeeze().dropna()
        d.index = pd.to_datetime(d.index).tz_localize(None).normalize(); px[etf] = d; BENCH[k] = etf; BLABEL[k] = lab + f' ({etf} proxy)'
BKEYS = [b[0] for b in BENCHES]

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

def windows(s, d, after_close=False):
    """dict horizon -> (start_date, end_date) using trading dates of s. d = mention date.
    after_close=True (post/remark after the 4 PM ET close): entry is the NEXT trading day, so day0 is the first session that could react."""
    after = s.index[s.index > d] if after_close else s.index[s.index >= d]
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
    r = dict(m); r.update(returns={}, ex={k: {} for k in BKEYS + ['btc']})
    t = m.get('ticker')
    if t and t.startswith('BASKET:'):
        s = basket_series(m)
        if s is not None: px[t] = s
    s = px.get(t) if t else None
    if s is None:
        r['status'] = m.get('note') or 'no price data'; rows.append(r); continue
    e, W = windows(s, pd.Timestamp(m['date']), bool(m.get('after_close')) and m['type'] != 'crypto')
    if e is None: r['status'] = 'no price after date'; rows.append(r); continue
    r.update(status='ok', entry_date=str(e.date()), entry_price=float(s.loc[e]))
    for k, (a, b) in W.items():
        v = ret(s, a, b); r['returns'][k] = v
        for key, bt in BENCH.items():
            if key == 'btc' and m['type'] != 'crypto': continue
            bv = ret(px[bt], a, b)
            if bv is not None: r['ex'][key][k] = v - bv
    sc = SEC['tickers'].get(t) if m['type'] == 'stock' else None
    if sc and sc['etf'] in px:  # same windows vs the stock's own SPDR sector ETF
        r['sector'] = dict(name=sc['sector'], industry=sc['industry'], etf=sc['etf'], ret={}, ex={})
        for k, (a, b) in W.items():
            sv = ret(px[sc['etf']], a, b)
            if sv is None: continue
            r['sector']['ret'][k] = sv
            if r['returns'].get(k) is not None: r['sector']['ex'][k] = r['returns'][k] - sv
        # tighter industry peer ETF when available (e.g. SMH for chips vs XLK for all tech)
        pe = sc.get('peer')
        if pe and pe in px:
            r['sector']['peer'] = pe
            r['sector']['peer_ret'] = {}
            r['sector']['peer_ex'] = {}
            for k, (a, b) in W.items():
                pv = ret(px[pe], a, b)
                if pv is None: continue
                r['sector']['peer_ret'][k] = pv
                if r['returns'].get(k) is not None: r['sector']['peer_ex'][k] = r['returns'][k] - pv
    if m.get('basket'):
        comp = []
        for ct, name in m['basket']:
            cs = px.get(ct)
            if cs is None: comp.append(dict(ticker=ct, name=name, returns={}, ex={k: {} for k in BKEYS})); continue
            cr = dict(ticker=ct, name=name, returns={}, ex={k: {} for k in BKEYS})
            for k, (a, b) in W.items():
                v = ret(cs, a, b)
                if v is None: continue
                cr['returns'][k] = v
                for key in BKEYS:
                    bv = ret(px[BENCH[key]], a, b)
                    if bv is not None: cr['ex'][key][k] = v - bv
            comp.append(cr)
        r['components'] = comp
    rows.append(r)
# Market-model (beta-adjusted) abnormal returns vs the S&P 500: beta from daily returns over the 250 S&P sessions
# ending 30 sessions before the entry day (so the comment itself and the run-up don't affect it). abnormal = return - beta * S&P return.
# Alpha is deliberately left out (it would extrapolate any pre-period trend). Needs >= 100 overlapping daily returns.
_spx = px[BENCH['sp']]
for r in rows:
    if r.get('status') != 'ok': continue
    s = px.get(r['ticker']); e = pd.Timestamp(r['entry_date'])
    si = _spx.index[_spx.index < e]
    if len(si) < 60: continue
    est = si[max(0, len(si) - 280):max(0, len(si) - 30)]
    if not len(est): continue
    al = s[(s.index >= est[0] - pd.Timedelta(days=7)) & (s.index <= est[-1])]
    if len(al) < 50: continue
    a2 = al.reindex(al.index.union(est)).ffill().reindex(est)
    df = pd.concat([a2.pct_change(), _spx.reindex(est).pct_change()], axis=1).dropna()
    df = df[(df.iloc[:, 0] != 0) | (df.iloc[:, 1] != 0)]
    if len(df) < 100 or df.iloc[:, 1].var() == 0: continue
    b = float(df.iloc[:, 0].cov(df.iloc[:, 1]) / df.iloc[:, 1].var())
    _, W = windows(s, pd.Timestamp(r['date']), bool(r.get('after_close')) and r['type'] != 'crypto')
    ab = {}
    for k in ('day0', '+1d', '+7d', '+30d', '+90d', 'to date'):
        if k in W and r['returns'].get(k) is not None:
            mv = ret(_spx, *W[k])
            if mv is not None: ab[k] = r['returns'][k] - b * mv
    r['beta'] = dict(b=round(b, 3), n=int(len(df)), start=str(est[0].date()), end=str(est[-1].date()))
    r['abn'] = ab
# Random-date (placebo) baseline: how did the SAME asset do vs the S&P 500 on ordinary days with no comment?
# Candidate entry days: the asset's trading days from 2 years before the mention to today, excluding +-30 calendar days
# around any tracked mention of that ticker. Stored as 40 equal-probability quantiles per window so the page can redraw it.
_mdates = {}
for r in rows:
    if r.get('status') == 'ok': _mdates.setdefault(r['ticker'], []).append(pd.Timestamp(r['entry_date']))
_qs = (np.arange(40) + 0.5) / 40  # midpoints of 40 equal-probability slices (each = 2.5% of days)
for r in rows:
    if r.get('status') != 'ok': continue
    s = px.get(r['ticker']); e = pd.Timestamp(r['entry_date'])
    sp_al = _spx.reindex(s.index.union(_spx.index)).ffill().reindex(s.index)
    idx = s.index; ok_d = (idx >= e - pd.Timedelta(days=730))
    for md in _mdates[r['ticker']]: ok_d &= ~((idx >= md - pd.Timedelta(days=30)) & (idx <= md + pd.Timedelta(days=30)))
    out = {}
    d0 = (s / s.shift(1) - 1) - (sp_al / sp_al.shift(1) - 1)
    v0 = d0[ok_d].dropna()
    tgt = idx + pd.Timedelta(days=30); j = idx.searchsorted(tgt)
    valid = j < len(idx); jj = np.where(valid, j, len(idx) - 1)
    r30 = pd.Series(np.where(valid, s.values[jj] / s.values - 1 - (sp_al.values[jj] / sp_al.values - 1), np.nan), index=idx)
    v30 = r30[ok_d].dropna()
    # pre-comment placebo: biggest of |-30d| and |-7d| excess vs S&P, both windows ending at the close before the entry day
    pm = {}
    for n in (30, 7):
        jn = idx.searchsorted(idx - pd.Timedelta(days=n), side='right') - 1
        pos = np.arange(len(idx)); vd = (jn >= 0) & (jn < pos - 1); jc = np.clip(jn, 0, None); pc = np.clip(pos - 1, 0, None)
        pm[n] = pd.Series(np.where(vd, s.values[pc] / s.values[jc] - 1 - (sp_al.values[pc] / sp_al.values[jc] - 1), np.nan), index=idx)
    vpre = pd.concat([pm[30].abs(), pm[7].abs()], axis=1).max(axis=1, skipna=True)[ok_d].dropna()
    a30, a7 = r['ex']['sp'].get('-30d'), r['ex']['sp'].get('-7d')
    if len(vpre) >= 60 and (a30 is not None or a7 is not None):
        act = max(abs(a30 or 0), abs(a7 or 0))
        out['pre'] = dict(q=[round(float(x), 5) for x in np.quantile(vpre.values, _qs)], n=int(len(vpre)), act=round(act, 5),
                          pct=round(float((vpre.values < act).mean() + 0.5 * (vpre.values == act).mean()), 3))
    for h, v in (('day0', v0), ('+30d', v30)):
        if len(v) < 60 or r['ex']['sp'].get(h) is None: continue
        act = r['ex']['sp'][h]
        out[h] = dict(q=[round(float(x), 5) for x in np.quantile(v.values, _qs)], mean=round(float(v.mean()), 5), n=int(len(v)),
                      pct=round(float((v.values < act).mean() + 0.5 * (v.values == act).mean()), 3))
    if out: r['plc'] = out
for r in rows:
    r['disclosures'] = [d for d in DISC if [r['date'], r.get('ticker')] in d['applies']]
    r['congress'] = [c for c in CONG if c['mention'] == [r['date'], r.get('ticker')]]
# same-post groups: one post naming several assets (same author, date and source URL) gets a shared id
_pg = {}
for r in rows: _pg.setdefault((r['who'], r['date'], r.get('source')), []).append(r)
_n = 0
for k, g in sorted(_pg.items(), key=lambda kv: kv[0][1]):
    if len(g) > 1:
        _n += 1
        for r in g: r['post'] = f'p{_n}'; r['post_n'] = len(g)
ok = [r for r in rows if r['status'] == 'ok']

# portfolios ($1,000 at entry close per priced mention) vs same cash flows into SPY and DIA
start = min(pd.Timestamp(r['entry_date']) for r in ok)
days = pd.date_range(start, TODAY, freq='D')
ff = {t: s.reindex(days.union(s.index)).ffill().reindex(days) for t, s in px.items()}
def curve(sel, hold=None):
    out = {k: pd.Series(0.0, index=days) for k in ['val', 'inv'] + BKEYS}
    for r in sel:
        d0 = pd.Timestamp(r['entry_date']); mask = days >= d0
        for key, ser in [('val', ff[r['ticker']])] + [(k, ff[BENCH[k]]) for k in BKEYS]:
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
    e0 = pd.Timestamp(r['entry_date']); r['b0'] = {k: float(asof(px[BENCH[k]], e0)) for k in BKEYS}
    r['curve'] = [None if (d < pd.Timestamp(r['entry_date']) or pd.isna(v)) else round(float(v), 4) for d, v in zip(grid, a)]
# weekly price history per priced ticker (for the ticker-lookup chart with mention markers) on one common weekly index
_wk = pd.date_range(pd.Timestamp(min(r['entry_date'] for r in ok)) - pd.Timedelta(days=120), TODAY, freq='W-FRI')
def _wser(s): return s.reindex(s.index.union(_wk)).ffill().reindex(_wk)
def _sig(x): return None if pd.isna(x) else float(f'{float(x):.5g}')
tkpx = {'dates': [str(d.date()) for d in _wk], 'bench': {k: [_sig(x) for x in _wser(px[BENCH[k]])] for k in BKEYS}, 'etf': {}, 't': {}}
for t in sorted({r['ticker'] for r in ok}):
    first = min(pd.Timestamp(r['date']) for r in ok if r['ticker'] == t) - pd.Timedelta(days=120)
    w = _wser(px[t]); i0 = max(int((_wk < first).sum()), int(w.isna().values.argmin()) if w.notna().any() else 0)
    tkpx['t'][t] = {'i0': i0, 'v': [_sig(x) for x in w.iloc[i0:]], 'last': [str(px[t].index[-1].date()), _sig(px[t].iloc[-1])]}
    _sc = SEC['tickers'].get(t) or {}
    for _k in ('etf', 'peer'):
        _e = _sc.get(_k)
        if _e and _e in px and len(px[_e]):
            tkpx['t'][t]['sec' if _k == 'etf' else 'peer'] = _e
            if _e not in tkpx['etf']: tkpx['etf'][_e] = [_sig(x) for x in _wser(px[_e])]
# family-linked listed companies vs indexes (context panel; not accusation)
def _ret_since(s, d0):
    a = asof(s, pd.Timestamp(d0)); b = float(s.iloc[-1]) if len(s) else None
    return None if a is None or b is None or a == 0 else float(b / a - 1)
_fam_wk = pd.date_range(pd.Timestamp('2024-03-01'), TODAY, freq='W-FRI')
fam_rows = []
for c in FAM['companies']:
    tkr = c['ticker']; s = px.get(tkr)
    row = dict(ticker=tkr, name=c['name'], link=c['link'], holding_source=c['holding_source'],
               milestones=[], last=None, ytd=None, ytd_sp=None)
    if s is not None and len(s):
        row['last'] = [str(s.index[-1].date()), _sig(s.iloc[-1])]
        y0 = f'{TODAY.year}-01-01'
        row['ytd'] = _ret_since(s, y0)
        row['ytd_sp'] = _ret_since(px[BENCH['sp']], y0) if 'sp' in BENCH else None
        for m in c['milestones']:
            mr = _ret_since(s, m['date']); br = _ret_since(px[BENCH['sp']], m['date']) if 'sp' in BENCH else None
            row['milestones'].append(dict(date=m['date'], label=m['label'], source=m['source'],
                                          ret=mr, ex=(None if mr is None or br is None else mr - br), bench=br))
        # weekly series for chart (DJT and peers), aligned
        w = s.reindex(s.index.union(_fam_wk)).ffill().reindex(_fam_wk)
        i0 = int(w.isna().values.argmin()) if w.notna().any() else 0
        row['wk'] = {'i0': i0, 'v': [_sig(x) for x in w.iloc[i0:]]}
    else:
        row['status'] = 'no price data'
        row['milestones'] = [dict(date=m['date'], label=m['label'], source=m['source'], ret=None, ex=None, bench=None) for m in c['milestones']]
    fam_rows.append(row)
fam_px = {'dates': [str(d.date()) for d in _fam_wk],
          'bench': {k: [_sig(x) for x in px[BENCH[k]].reindex(px[BENCH[k]].index.union(_fam_wk)).ffill().reindex(_fam_wk)] for k in BKEYS},
          'note': FAM['_note'], 'rows': fam_rows}

gridd = dict(dates=[str(d.date()) for d in grid], **{k: [round(float(x), 3) for x in ff[BENCH[k]].reindex(grid)] for k in BKEYS})
data = dict(grid=gridd, generated=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), horizons=HOR,
            rows=rows, exclusions=EX, disclosure_notes=DNOTES, benches=[[k, BLABEL[k], BENCH[k]] for k in BKEYS], portfolio=port, group_portfolio=gport, tkpx=tkpx, sector_note=SEC['_note'], sector_etfs=SEC['etf_names'], peer_etfs=SEC.get('peer_etf_names', {}), family=fam_px)
json.dump(data, open(f'{HERE}/data.json', 'w'), indent=1, default=float)
html = open(f'{HERE}/template.html').read()
html = html.replace('/*__DATA__*/null', json.dumps(data, default=float)).replace('/*__CHARTJS__*/', open(f'{HERE}/chart.umd.min.js').read())
open(f'{HERE}/index.html', 'w').write(html)
print('mentions', len(rows), 'priced', len(ok))
