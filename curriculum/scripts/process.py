import csv, json, datetime, statistics, os

D = os.path.dirname(os.path.abspath(__file__))

def read_fred(fname, series):
    path = os.path.join(D, fname)
    out = []
    with open(path, newline='') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            if len(row) < 2:
                continue
            date, val = row[0], row[1]
            if val == '.' or val == '':
                continue
            try:
                out.append((date, float(val)))
            except ValueError:
                continue
    return out

def read_yahoo(fname):
    path = os.path.join(D, fname)
    with open(path) as f:
        j = json.load(f)
    res = j['chart']['result'][0]
    ts = res['timestamp']
    closes = res['indicators']['quote'][0]['close']
    out = []
    for t, c in zip(ts, closes):
        if c is None:
            continue
        d = datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d')
        out.append((d, round(c, 4)))
    return out

def to_month_key(d):
    return d[:7]  # YYYY-MM

def monthly_last(series):
    """Downsample a daily/weekly series to monthly using the last observation of each month."""
    by_month = {}
    for d, v in series:
        by_month[to_month_key(d)] = v  # relies on series being chronological; overwritten by later = last
    return sorted(by_month.items())

def monthly_avg(series):
    by_month = {}
    for d, v in series:
        by_month.setdefault(to_month_key(d), []).append(v)
    return sorted((k, round(statistics.mean(v), 4)) for k, v in by_month.items())

def monthly_min_with_date(series):
    """Return monthly series using the MIN value in each month, keeping the exact date of that min."""
    by_month = {}
    for d, v in series:
        k = to_month_key(d)
        if k not in by_month or v < by_month[k][1]:
            by_month[k] = (d, v)
    return sorted(by_month.items())  # k -> (date, val)

def yoy(monthly_series):
    """monthly_series: list of (YYYY-MM, val) sorted. Returns YoY % list."""
    idx = {k: v for k, v in monthly_series}
    out = []
    for k, v in monthly_series:
        y, m = int(k[:4]), int(k[5:7])
        py = f'{y-1:04d}-{m:02d}'
        if py in idx and idx[py] != 0:
            out.append((k, round((v / idx[py] - 1) * 100, 2)))
    return out

def recession_bands(usrec):
    """usrec: list of (YYYY-MM-DD, 0/1 monthly). Returns list of [start, end] month ranges where val==1."""
    bands = []
    cur_start = None
    prev_month = None
    for d, v in usrec:
        m = to_month_key(d)
        if v >= 1:
            if cur_start is None:
                cur_start = m
            prev_month = m
        else:
            if cur_start is not None:
                bands.append([cur_start, prev_month])
                cur_start = None
    if cur_start is not None:
        bands.append([cur_start, prev_month])
    return bands

def clip(series, start=None, end=None):
    return [(k, v) for k, v in series if (start is None or k >= start) and (end is None or k <= end)]

def fmt(series):
    return [{'t': k, 'v': v} for k, v in series]

# ---- Load raw ----
fedfunds = read_fred('FEDFUNDS.csv', 'FEDFUNDS')          # monthly since 1954
dexkous = read_fred('DEXKOUS.csv', 'DEXKOUS')              # daily since 1981
sp500_fred = read_fred('SP500.csv', 'SP500')                # daily since 2016
t10y2y = read_fred('T10Y2Y.csv', 'T10Y2Y')                  # daily since 1976
usrec = read_fred('USREC.csv', 'USREC')                     # monthly since 1854
oil = read_fred('DCOILWTICO.csv', 'DCOILWTICO')             # daily since 1986
cpi_raw = read_fred('CPIAUCSL.csv', 'CPIAUCSL')             # monthly since 1947
cpi = monthly_last(cpi_raw)                                  # normalize date keys to YYYY-MM
m2 = read_fred('M2SL.csv', 'M2SL')                          # monthly since 1959
dxy = read_fred('DTWEXBGS.csv', 'DTWEXBGS')                 # daily since 2006

kospi = read_yahoo('yh_KS11_full.json')     # monthly
kosdaq = read_yahoo('yh_KQ11_full.json')    # monthly
gold = read_yahoo('yh_GC_full.json')        # monthly since ~2000
btc = read_yahoo('yh_BTC_full.json')        # monthly since ~2014
gspc = read_yahoo('yh_GSPC_full.json')      # monthly, long history since 1985

print('raw ranges:')
for name, s in [('fedfunds', fedfunds), ('dexkous', dexkous), ('sp500_fred', sp500_fred),
                 ('t10y2y', t10y2y), ('usrec', usrec), ('oil', oil), ('cpi', cpi), ('m2', m2),
                 ('dxy', dxy), ('kospi', kospi), ('kosdaq', kosdaq), ('gold', gold), ('btc', btc), ('gspc', gspc)]:
    print(f'  {name}: {s[0][0]} ~ {s[-1][0]}  ({len(s)} rows)')

# ---- Derived / monthly ----
fedfunds_m = monthly_last(fedfunds)  # normalize date keys to YYYY-MM
dexkous_m = monthly_last(dexkous)
gspc_m = monthly_last(gspc)
sp500_fred_m = monthly_last(sp500_fred)
t10y2y_m = monthly_last(t10y2y)
oil_m_last = monthly_last(oil)
oil_m_min = monthly_min_with_date(oil)  # (month -> (exact_date, min_val))
cpi_yoy = yoy(cpi)
m2_m = monthly_last(m2)  # normalize date keys to YYYY-MM
dxy_m = monthly_last(dxy)
kospi_m = monthly_last(kospi)
kosdaq_m = monthly_last(kosdaq)
gold_m = monthly_last(gold)
btc_m = monthly_last(btc)

bands = recession_bands(usrec)
bands_recent = [b for b in bands if b[1] >= '1970-01']
print('\nrecession bands (>=1970):', bands_recent)

# find exact oil min for annotation
oil_all_min = min(oil, key=lambda x: x[1])
print('\noil global min:', oil_all_min)

# ---- Build case datasets ----
case1 = {
    'title': '기준금리 vs 원/달러 환율 vs S&P500',
    'range': ['2003-01', None],
    'series': {
        'fedfunds': fmt(clip(fedfunds_m, '2003-01')),
        'usdkrw': fmt(clip(dexkous_m, '2003-01')),
        'sp500': fmt(clip(gspc_m, '2003-01')),
    }
}

case2 = {
    'title': '장단기 금리차(10Y-2Y) vs 경기침체',
    'range': ['1976-06', None],
    'series': {
        't10y2y': fmt(t10y2y_m),
    },
    'recessions': bands_recent,
}

case3_oil_monthly = clip(oil_m_last, '1986-01')
case3 = {
    'title': '유가(WTI) vs 소비자물가(CPI, YoY)',
    'range': ['1986-01', None],
    'series': {
        'oil': fmt(case3_oil_monthly),
        'cpi_yoy': fmt(clip(cpi_yoy, '1986-01')),
    },
    'oil_min_event': {'date': oil_all_min[0], 'value': oil_all_min[1]},
}

case4 = {
    'title': 'M2 통화량 vs 자산가격(S&P500 · 비트코인)',
    'range': ['2005-01', None],
    'series': {
        'm2': fmt(clip(m2_m, '2005-01')),
        'sp500': fmt(clip(gspc_m, '2005-01')),
        'btc': fmt(btc_m),
    }
}

case5_start = max(dxy_m[0][0], '2006-01')
case5 = {
    'title': '미국 기준금리 · 달러인덱스 vs 코스피 · 코스닥',
    'range': [case5_start, None],
    'series': {
        'fedfunds': fmt(clip(fedfunds_m, case5_start)),
        'dxy': fmt(clip(dxy_m, case5_start)),
        'kospi': fmt(clip(kospi_m, case5_start)),
        'kosdaq': fmt(clip(kosdaq_m, case5_start)),
    }
}

case6_start = btc_m[0][0]
case6 = {
    'title': '금 · 비트코인 vs 달러인덱스',
    'range': [case6_start, None],
    'series': {
        'gold': fmt(clip(gold_m, case6_start)),
        'btc': fmt(btc_m),
        'dxy': fmt(clip(dxy_m, case6_start)),
    }
}

data = {
    'case1': case1, 'case2': case2, 'case3': case3, 'case4': case4, 'case5': case5, 'case6': case6,
    'meta': {
        'sources': {
            'fedfunds': 'FRED FEDFUNDS (Effective Federal Funds Rate, monthly)',
            'usdkrw': 'FRED DEXKOUS (KRW/USD, daily->monthly last)',
            'sp500': 'Yahoo Finance ^GSPC (weekly->monthly last)',
            't10y2y': 'FRED T10Y2Y (10Y-2Y Treasury spread, daily->monthly last)',
            'recessions': 'FRED USREC (NBER recession indicator)',
            'oil': 'FRED DCOILWTICO (WTI spot, daily->monthly last)',
            'cpi': 'FRED CPIAUCSL (CPI-U, YoY % computed)',
            'm2': 'FRED M2SL (M2 money stock, monthly)',
            'btc': 'Yahoo Finance BTC-USD (weekly->monthly last)',
            'dxy': 'FRED DTWEXBGS (Trade-weighted USD index, daily->monthly last)',
            'kospi': 'Yahoo Finance ^KS11 (weekly->monthly last)',
            'kosdaq': 'Yahoo Finance ^KQ11 (weekly->monthly last)',
            'gold': 'Yahoo Finance GC=F (COMEX gold futures, weekly->monthly last)',
        }
    }
}

out_path = os.path.join(D, 'data.json')
with open(out_path, 'w') as f:
    json.dump(data, f, separators=(',', ':'))
print('\nwrote', out_path, os.path.getsize(out_path), 'bytes')

# print counts per case
for cname in ['case1','case2','case3','case4','case5','case6']:
    c = data[cname]
    print(cname, {k: len(v) for k, v in c['series'].items()})
