import json, os
D = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(D, 'data.json')))

def series(case, key):
    return {p['t']: p['v'] for p in data[case]['series'][key]}

def get(case, key, month, nearest=True):
    s = series(case, key)
    if month in s:
        return month, s[month]
    if nearest:
        ks = sorted(s.keys())
        best = min(ks, key=lambda k: abs(_mi(k)-_mi(month)))
        return best, s[best]
    return None, None

def _mi(t):
    y,m = t.split('-'); return int(y)*12+int(m)

def pct(a,b):
    return round((b/a-1)*100,1)

print('=== case7 WALCL vs SP500 ===')
for m in ['2008-08','2008-11','2009-06','2020-02','2020-06','2022-04','2023-03','2026-07']:
    print(' walcl', get('case7','walcl',m), '| sp500', get('case7','sp500',m))

print('=== case8 wage_yoy vs cpi_yoy ===')
for m in ['2015-01','2019-12','2021-01','2021-12','2022-06','2022-12','2023-06','2024-06','2026-07']:
    print(' wage', get('case8','wage_yoy',m), '| cpi', get('case8','cpi_yoy',m))

print('=== case9 baa10y vs sp500 ===')
for m in ['2007-06','2008-12','2009-03','2020-02','2020-03','2020-04','2022-01','2022-10']:
    print(' baa10y', get('case9','baa10y',m), '| sp500', get('case9','sp500',m))
mx = max(data['case9']['series']['baa10y'], key=lambda p:p['v'])
print(' baa10y all-time max in this window:', mx)

print('=== case10 dxyem vs eem ===')
for m in ['2013-04','2013-09','2015-07','2015-09','2021-12','2022-10','2026-07']:
    print(' dxyem', get('case10','dxyem',m), '| eem', get('case10','eem',m))

print('=== case11 usdkrw vs kospi ===')
for m in ['1997-06','1997-11','1997-12','1998-01','1998-06','2008-08','2008-11','2009-03','2021-12','2022-10','2023-01']:
    print(' usdkrw', get('case11','usdkrw',m), '| kospi', get('case11','kospi',m))

print('=== case12 sox vs kospi ===')
for m in ['2000-03','2000-12','2008-08','2008-11','2018-06','2018-12','2022-01','2022-10','2023-12','2024-12','2026-07']:
    print(' sox', get('case12','sox',m), '| kospi', get('case12','kospi',m))

print('=== case13 vix vs sp500 ===')
for m in ['2008-08','2008-11','2009-03','2020-02','2020-03','2020-04','2022-01','2022-10']:
    print(' vix', get('case13','vix',m), '| sp500', get('case13','sp500',m))
mx = max(data['case13']['series']['vix'], key=lambda p:p['v'])
print(' vix window max:', mx)
