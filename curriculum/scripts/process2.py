import csv, json, datetime, statistics, os

D = os.path.dirname(os.path.abspath(__file__))

def read_fred(fname):
    path = os.path.join(D, fname)
    out = []
    with open(path, newline='') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            if len(row) < 2:
                continue
            date, val = row[0], row[1]
            if val in ('.', ''):
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
    return d[:7]

def monthly_last(series):
    by_month = {}
    for d, v in series:
        by_month[to_month_key(d)] = v
    return sorted(by_month.items())

def monthly_max_with_date(series):
    by_month = {}
    for d, v in series:
        k = to_month_key(d)
        if k not in by_month or v > by_month[k][1]:
            by_month[k] = (d, v)
    return sorted(by_month.items())

def yoy(monthly_series):
    idx = {k: v for k, v in monthly_series}
    out = []
    for k, v in monthly_series:
        y, m = int(k[:4]), int(k[5:7])
        py = f'{y-1:04d}-{m:02d}'
        if py in idx and idx[py] != 0:
            out.append((k, round((v / idx[py] - 1) * 100, 2)))
    return out

def clip(series, start=None, end=None):
    return [(k, v) for k, v in series if (start is None or k >= start) and (end is None or k <= end)]

def fmt(series):
    return [{'t': k, 'v': v} for k, v in series]

# ---- load new raw series ----
walcl_raw = read_fred('WALCL.csv')                  # weekly, millions $, since 2002-12-18
ahetpi_raw = read_fred('AHETPI.csv')                # monthly $/hr, since 1964
cpi_raw = read_fred('CPIAUCSL.csv')                 # monthly, since 1947
baa10y_raw = read_fred('BAA10Y.csv')                # daily %, since 1986 (Baa - 10Y spread, credit-risk proxy)
dxyem_raw = read_fred('DTWEXEMEGS.csv')             # daily, since 2006
vix_raw = read_fred('VIXCLS.csv')                   # daily, since 1990
dexkous_raw = read_fred('DEXKOUS.csv')              # daily, since 1981

sox = read_yahoo('yh_SOX_full.json')                # weekly, since 1994
eem = read_yahoo('yh_EEM_full.json')                # weekly, since 2003
kospi = read_yahoo('yh_KS11_full.json')             # weekly, since 1996
gspc = read_yahoo('yh_GSPC_full.json')              # weekly, long history

walcl_m = monthly_last(walcl_raw)
walcl_m = [(k, round(v/1000.0, 1)) for k, v in walcl_m]   # millions -> billions (so unit '$B' formatter shows $X.XT)
cpi_m = monthly_last(cpi_raw)
cpi_yoy = yoy(cpi_m)
ahetpi_m = monthly_last(ahetpi_raw)
ahetpi_yoy = yoy(ahetpi_m)
baa10y_m = monthly_last(baa10y_raw)
dxyem_m = monthly_last(dxyem_raw)
vix_m = monthly_last(vix_raw)
vix_m_peak = monthly_max_with_date(vix_raw)
dexkous_m = monthly_last(dexkous_raw)
sox_m = monthly_last(sox)
eem_m = monthly_last(eem)
kospi_m = monthly_last(kospi)
gspc_m = monthly_last(gspc)

print('ranges:')
for name, s in [('walcl_m', walcl_m), ('cpi_yoy', cpi_yoy), ('ahetpi_yoy', ahetpi_yoy),
                 ('baa10y_m', baa10y_m), ('dxyem_m', dxyem_m), ('vix_m', vix_m),
                 ('dexkous_m', dexkous_m), ('sox_m', sox_m), ('eem_m', eem_m), ('kospi_m', kospi_m)]:
    print(f'  {name}: {s[0][0]} ~ {s[-1][0]} ({len(s)} rows)')

vix_all_peak = max(vix_raw, key=lambda x: x[1])
print('\nVIX all-time peak:', vix_all_peak)
walcl_2020 = [v for k, v in walcl_m if '2020-02' <= k <= '2020-06']
print('WALCL 2020-02..06:', walcl_2020)

case7_start = '2007-01'
case7 = {
    'title': "연준 대차대조표(QE·QT) vs S&P500",
    'range': [case7_start, None],
    'series': {
        'walcl': fmt(clip(walcl_m, case7_start)),
        'sp500': fmt(clip(gspc_m, case7_start)),
    }
}

case8_start = '2015-01'
case8 = {
    'title': '시간당 임금 상승률 vs CPI 상승률 (YoY)',
    'range': [case8_start, None],
    'series': {
        'wage_yoy': fmt(clip(ahetpi_yoy, case8_start)),
        'cpi_yoy': fmt(clip(cpi_yoy, case8_start)),
    }
}

case9_start = '1986-01'
case9 = {
    'title': '신용스프레드(Baa회사채-10Y국채) vs S&P500',
    'range': [case9_start, None],
    'series': {
        'baa10y': fmt(clip(baa10y_m, case9_start)),
        'sp500': fmt(clip(gspc_m, case9_start)),
    }
}

case10_start = max(dxyem_m[0][0], eem_m[0][0])
case10 = {
    'title': '신흥국 달러인덱스 vs 신흥국 주식(EEM)',
    'range': [case10_start, None],
    'series': {
        'dxyem': fmt(clip(dxyem_m, case10_start)),
        'eem': fmt(clip(eem_m, case10_start)),
    }
}

case11_start = max(dexkous_m[0][0], kospi_m[0][0], '1997-01')
case11 = {
    'title': '원/달러 환율 vs 코스피',
    'range': [case11_start, None],
    'series': {
        'usdkrw': fmt(clip(dexkous_m, case11_start)),
        'kospi': fmt(clip(kospi_m, case11_start)),
    }
}

case12_start = max(sox_m[0][0], kospi_m[0][0])
case12 = {
    'title': '필라델피아 반도체지수(SOX) vs 코스피',
    'range': [case12_start, None],
    'series': {
        'sox': fmt(clip(sox_m, case12_start)),
        'kospi': fmt(clip(kospi_m, case12_start)),
    }
}

case13_start = '1990-01'
case13 = {
    'title': 'VIX(변동성지수) vs S&P500',
    'range': [case13_start, None],
    'series': {
        'vix': fmt(clip(vix_m, case13_start)),
        'sp500': fmt(clip(gspc_m, case13_start)),
    }
}

new_cases = {
    'case7': case7, 'case8': case8, 'case9': case9, 'case10': case10,
    'case11': case11, 'case12': case12, 'case13': case13,
}

new_sources = {
    'walcl': 'FRED WALCL (연준 총자산, 주간->월간 마지막값, 십억달러)',
    'wage_yoy': 'FRED AHETPI (시간당 평균임금, 전년동월대비 직접계산)',
    'cpi_yoy2': 'FRED CPIAUCSL (전년동월대비, case3과 동일 시리즈)',
    'baa10y': 'FRED BAA10Y (무디스 Baa 회사채 - 10년 국채 스프레드, 일간->월간 마지막값)',
    'dxyem': 'FRED DTWEXEMEGS (신흥국 대상 명목 달러지수, 일간->월간 마지막값)',
    'eem': 'Yahoo Finance EEM (iShares MSCI Emerging Markets ETF, 주간->월간 마지막값)',
    'usdkrw2': 'FRED DEXKOUS (원/달러, case1과 동일 시리즈)',
    'sox': 'Yahoo Finance ^SOX (필라델피아 반도체지수, 주간->월간 마지막값)',
    'vix': 'FRED VIXCLS (CBOE 변동성지수, 일간->월간 마지막값)',
}

existing = json.load(open(os.path.join(D, 'data.json')))
existing.update(new_cases)
existing['meta']['sources'].update(new_sources)

out_path = os.path.join(D, 'data.json')
with open(out_path, 'w') as f:
    json.dump(existing, f, separators=(',', ':'))
print('\nwrote', out_path, os.path.getsize(out_path), 'bytes')
for cname in new_cases:
    c = new_cases[cname]
    print(cname, c['range'], {k: len(v) for k, v in c['series'].items()})
