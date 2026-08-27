#!/usr/bin/env python3
"""Market Note local server: static files, public market APIs, SQLite cache."""
from __future__ import annotations

import json, os, sqlite3, time
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlencode, urlparse
import requests

ROOT = Path(__file__).resolve().parent
DB = ROOT / "market_note.db"

def load_local_env():
    """Load simple KEY=VALUE pairs from .env without an extra dependency."""
    path = ROOT / ".env"
    if not path.exists(): return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ: os.environ[key] = value

load_local_env()
PORT = int(os.getenv("MARKET_NOTE_PORT", "4173"))
UA = os.getenv("MARKET_NOTE_USER_AGENT", "MarketNote/0.1 contact@example.com")

def env(name): return os.getenv(name, "").strip()
def now(): return datetime.now(timezone.utc).isoformat()

def db():
    con = sqlite3.connect(DB)
    con.execute("create table if not exists cache(key text primary key, value text, updated real)")
    con.execute("create table if not exists predictions(id integer primary key, created text, thesis text, probability integer, invalidation text, result text default '')")
    return con

def cached(key, ttl, loader):
    con = db(); row = con.execute("select value,updated from cache where key=?", (key,)).fetchone()
    if row and time.time() - row[1] < ttl:
        prior = json.loads(row[0])
        if prior.get("connected") is not False and not prior.get("error"):
            con.close(); return prior, "cache"
    try:
        value = loader(); con.execute("insert or replace into cache values(?,?,?)", (key, json.dumps(value, ensure_ascii=False), time.time())); con.commit(); con.close(); return value, "live"
    except Exception as exc:
        con.close()
        if row: return json.loads(row[0]), "stale"
        return {"error": str(exc)}, "error"

def get_json(url, params=None, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json"}; h.update(headers or {})
    r = requests.get(url, params=params, headers=h, timeout=15); r.raise_for_status(); return r.json()

def fred():
    key = env("FRED_API_KEY")
    if not key: return {"connected": False, "reason": "FRED_API_KEY 필요"}
    series = {"DGS10":"미 10년물", "DFF":"연방기금금리", "DTWEXBGS":"달러지수", "VIXCLS":"VIX"}; out=[]
    for sid, label in series.items():
        data=get_json("https://api.stlouisfed.org/fred/series/observations", {"series_id":sid,"api_key":key,"file_type":"json","sort_order":"desc","limit":8})
        vals=[x for x in data.get("observations",[]) if x.get("value") != "."]
        if vals: out.append({"id":sid,"label":label,"value":float(vals[0]["value"]),"date":vals[0]["date"],"history":[float(x["value"]) for x in reversed(vals)]})
    return {"connected": True, "series": out}

def dart():
    key=env("DART_API_KEY")
    if not key: return {"connected":False,"reason":"DART_API_KEY 필요"}
    end=datetime.now().strftime("%Y%m%d"); start=datetime.fromtimestamp(time.time()-7*86400).strftime("%Y%m%d")
    data=get_json("https://opendart.fss.or.kr/api/list.json", {"crtfc_key":key,"bgn_de":start,"end_de":end,"page_count":20})
    return {"connected":data.get("status")=="000","items":data.get("list",[]),"message":data.get("message")}

def korea_prices():
    key=unquote(env("DATA_GO_KR_KEY"))
    if not key: return {"connected":False,"reason":"DATA_GO_KR_KEY 필요"}
    data=get_json("https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo", {"serviceKey":key,"numOfRows":50,"pageNo":1,"resultType":"json"})
    body=data.get("response",{}).get("body",{}); items=body.get("items",{}).get("item",[])
    return {"connected":True,"items":items,"total":body.get("totalCount",0)}

def sec():
    companies={"AAPL":"0000320193","MSFT":"0000789019","NVDA":"0001045810"}; items=[]
    for ticker,cik in companies.items():
        d=get_json(f"https://data.sec.gov/submissions/CIK{cik}.json")
        recent=d.get("filings",{}).get("recent",{}); forms=recent.get("form",[])
        for i,form in enumerate(forms[:15]):
            if form in ("10-K","10-Q","8-K"):
                items.append({"ticker":ticker,"company":d.get("name"),"form":form,"date":recent["filingDate"][i],"accession":recent["accessionNumber"][i]}); break
    return {"connected":True,"items":items}

def telegram():
    token=env("TELEGRAM_BOT_TOKEN")
    if not token: return {"connected":False,"reason":"TELEGRAM_BOT_TOKEN 필요"}
    d=get_json(f"https://api.telegram.org/bot{token}/getUpdates", {"limit":100,"timeout":0})
    msgs=[]
    for u in d.get("result",[]):
        m=u.get("channel_post") or u.get("message") or {}; text=m.get("text") or m.get("caption")
        if text: msgs.append({"id":m.get("message_id"),"date":m.get("date"),"chat":m.get("chat",{}).get("title") or m.get("chat",{}).get("username","개인"),"text":text[:1000]})
    return {"connected":True,"count":len(msgs),"items":msgs[-30:]}

LOADERS={"fred":(3600,fred),"dart":(900,dart),"korea":(21600,korea_prices),"sec":(3600,sec),"telegram":(300,telegram)}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_json(self,obj,status=200):
        raw=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        if path == "/api/status":
            result={"updated_at":now(),"sources":{}}
            for name,(ttl,loader) in LOADERS.items():
                value,mode=cached(name,ttl,loader); result["sources"][name]={"mode":mode,**value}
            return self.send_json(result)
        if path == "/api/predictions":
            con=db(); rows=con.execute("select id,created,thesis,probability,invalidation,result from predictions order by id desc limit 30").fetchall(); con.close()
            return self.send_json({"items":[dict(zip(("id","created","thesis","probability","invalidation","result"),r)) for r in rows]})
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path != "/api/predictions": return self.send_json({"error":"not found"},404)
        length=int(self.headers.get("Content-Length","0")); payload=json.loads(self.rfile.read(length) or b"{}")
        thesis=str(payload.get("thesis","")).strip(); invalid=str(payload.get("invalidation","")).strip(); probability=max(1,min(99,int(payload.get("probability",50))))
        if not thesis or not invalid: return self.send_json({"error":"판단과 무효화 조건이 필요합니다."},400)
        con=db(); cur=con.execute("insert into predictions(created,thesis,probability,invalidation) values(?,?,?,?)",(now(),thesis,probability,invalid)); con.commit(); con.close(); return self.send_json({"ok":True,"id":cur.lastrowid},201)

if __name__ == "__main__":
    print(f"Market Note: http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1",PORT),Handler).serve_forever()
