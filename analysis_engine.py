"""Pure calculations for evidence-based long-horizon market analysis."""
from __future__ import annotations
from datetime import datetime
from statistics import mean, pstdev

def num(value, default=0.0):
    try: return float(str(value).replace(",", ""))
    except (TypeError, ValueError): return default

def normalize_bars(items):
    bars=[]
    for x in items:
        close=num(x.get("clpr"));
        if not close: continue
        bars.append({"date":x.get("basDt"),"close":close,"open":num(x.get("mkp")),"high":num(x.get("hipr")),"low":num(x.get("lopr")),"volume":num(x.get("trqu")),"turnover":num(x.get("trPrc"))})
    bars.sort(key=lambda x:x["date"])
    return bars

def prior_value(bars, sessions):
    return bars[max(0, len(bars)-1-sessions)]["close"] if bars else 0

def pct(a,b): return round((a/b-1)*100,2) if b else None

def company_metrics(name, code, bars):
    if len(bars)<30: return {"name":name,"code":code,"error":"insufficient history"}
    closes=[x["close"] for x in bars]; current=closes[-1]; peak=max(closes); low=min(closes)
    ma50=mean(closes[-50:]); ma200=mean(closes[-200:]) if len(closes)>=200 else mean(closes)
    returns=[closes[i]/closes[i-1]-1 for i in range(1,len(closes))]
    events=[]
    for i in range(20,len(bars)):
        r=returns[i-1]*100; base=mean([x["turnover"] for x in bars[i-20:i]])
        multiple=bars[i]["turnover"]/base if base else 0
        if r <= -3 or (r <= -2 and multiple >= 1.5): events.append({"date":bars[i]["date"],"return":round(r,2),"turnover_multiple":round(multiple,2),"close":bars[i]["close"]})
    events=sorted(events,key=lambda x:(x["return"],-x["turnover_multiple"]))[:8]
    recent=returns[-60:] if len(returns)>=60 else returns
    phase="확장"
    if current < ma200: phase="하락/기반 형성"
    elif ma50 < ma200: phase="회복 초기"
    elif pct(current,prior_value(bars,63)) and pct(current,prior_value(bars,63)) < 0: phase="상승 추세 내 둔화"
    elif pct(current,peak) is not None and pct(current,peak) > -5: phase="고점권 확산"
    return {"name":name,"code":code,"as_of":bars[-1]["date"],"sessions":len(bars),"current":current,"returns":{"1m":pct(current,prior_value(bars,21)),"3m":pct(current,prior_value(bars,63)),"1y":pct(current,prior_value(bars,252)),"2y":pct(current,bars[0]["close"])},"drawdown":pct(current,peak),"range_position":round((current-low)/(peak-low)*100,1) if peak>low else 0,"ma50":round(ma50,1),"ma200":round(ma200,1),"above_ma50":current>ma50,"above_ma200":current>ma200,"annualized_volatility":round(pstdev(recent)*(252**.5)*100,1) if len(recent)>1 else 0,"phase":phase,"sell_events":events,"series":[{"date":x["date"],"close":x["close"]} for x in bars[::max(1,len(bars)//120)]] + [{"date":bars[-1]["date"],"close":current}]}

def nearest_macro(date, macro_series, window=3):
    target=datetime.strptime(date,"%Y%m%d").date(); result=[]
    for series in macro_series:
        observations=series.get("observations",[]); nearest=None
        for obs in observations:
            try: delta=abs((datetime.strptime(obs["date"],"%Y-%m-%d").date()-target).days)
            except Exception: continue
            if delta<=window and (nearest is None or delta<nearest[0]): nearest=(delta,obs)
        if nearest: result.append({"id":series["id"],"label":series["label"],**nearest[1]})
    return result

def attach_evidence(metrics, disclosures, macro_series):
    for event in metrics.get("sell_events",[]):
        target=datetime.strptime(event["date"],"%Y%m%d").date(); related=[]
        for d in disclosures:
            try: gap=abs((datetime.strptime(d.get("rcept_dt",""),"%Y%m%d").date()-target).days)
            except Exception: continue
            if gap<=5: related.append({"date":d.get("rcept_dt"),"title":d.get("report_nm"),"receipt":d.get("rcept_no"),"distance_days":gap})
        event["disclosures"]=related[:5]; event["macro"]=nearest_macro(event["date"],macro_series)
        event["classification"]="확인 필요"
        if event["turnover_multiple"]>=1.8: event["classification"]="고거래대금 매도 압력"
        if related: event["classification"]="공시 인접 매도 반응"
    return metrics

def pair_conclusion(companies):
    valid=[x for x in companies if not x.get("error")]
    if len(valid)<2: return "장기 가격 데이터가 충분하지 않습니다."
    leader=max(valid,key=lambda x:x["returns"].get("1y") or -999); laggard=min(valid,key=lambda x:x["returns"].get("1y") or 999)
    spread=round((leader["returns"].get("1y") or 0)-(laggard["returns"].get("1y") or 0),2)
    return f"최근 1년 반도체 대형주 내부에서는 {leader['name']}의 상대 흐름이 우세하며 두 기업의 수익률 격차는 {spread}%p입니다. 섹터 전체 강세로 단정하기보다 이 격차가 축소되는지, 후행 기업도 200일선 위에서 거래대금을 동반해 회복하는지 확인해야 확산으로 볼 수 있습니다."
