from __future__ import annotations

import csv
import io
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

_configured_mode = os.getenv("NETWATCH_MODE", "demo").lower()
MODE = _configured_mode if _configured_mode in {"demo", "imported"} else "unavailable"
API_TOKEN = os.getenv("NETWATCH_INGEST_TOKEN", "")
STARTED = time.time()
app = FastAPI(title="SEGONE NetWatch API", version="0.1.0", description="Local-first defensive network visibility. Demo records are fictional.")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_methods=["GET", "POST", "PATCH"], allow_headers=["Content-Type", "Authorization"])

now = datetime.now(timezone.utc).replace(microsecond=0)
EVENTS: list[dict] = []
for i, (kind, src, dst, proto, size, domain) in enumerate([
    ("dns", "192.0.2.10", "192.0.2.53", "UDP", 92, "updates.example.test"),
    ("connection", "192.0.2.10", "198.51.100.24", "HTTPS", 18420, None),
    ("dns", "192.0.2.12", "192.0.2.53", "UDP", 88, "docs.example.test"),
    ("connection", "192.0.2.12", "203.0.113.18", "HTTPS", 6720, None),
    ("dns", "192.0.2.11", "192.0.2.53", "UDP", 102, "media.example.test"),
    ("connection", "192.0.2.11", "198.51.100.41", "HTTPS", 39100, None),
]):
    EVENTS.append({"id": f"demo-{i+1}", "timestamp": (now-timedelta(minutes=5-i)).isoformat(), "event_type": kind,
        "source_ip": src, "destination_ip": dst, "protocol": proto, "bytes": size, "domain": domain,
        "source": "deterministic_demo_fixture", "provenance": "demo", "confidence": "fictional"})

ALERTS = [{"id":"demo-alert-1", "rule_id":"demo.high_volume", "timestamp":now.isoformat(), "severity":"medium", "status":"open", "title":"Elevated sample transfer", "explanation":"Fictional demo event illustrating a high-volume alert.", "source":"demo", "evidence":["demo-6"]}]

class IngestEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=128)
    timestamp: datetime
    event_type: str = Field(min_length=1, max_length=40)
    source_ip: str | None = None
    destination_ip: str | None = None
    protocol: str | None = None
    bytes: int | None = Field(default=None, ge=0)
    domain: str | None = Field(default=None, max_length=253)
    source: str = Field(min_length=1, max_length=80)
    provenance: Literal["imported"]

class IngestBatch(BaseModel):
    events: list[IngestEvent] = Field(max_length=500)

def require_ingest_auth(authorization: str | None = Header(default=None)) -> None:
    if not API_TOKEN:
        raise HTTPException(503, "Ingestion is disabled: configure NETWATCH_INGEST_TOKEN.")
    expected = f"Bearer {API_TOKEN}"
    if authorization is None or not secrets.compare_digest(authorization, expected):
        raise HTTPException(401, "Invalid collector credentials.")

@app.get("/api/v1/health")
def health():
    return {"application": "healthy", "mode": MODE, "uptime_seconds": int(time.time()-STARTED), "collector": "unverified", "telemetry_freshness": None}

@app.get("/api/v1/system/status")
def system_status():
    return {"mode": MODE, "provenance": MODE, "listening": "127.0.0.1", "collector_operational": False, "source": None, "notice": "No live telemetry source has been configured or verified."}

@app.get("/api/v1/collector/status")
def collector_status():
    return {"status":"unavailable", "source":None, "interface":None, "last_event_at":None, "queue_depth":0, "dropped_events":0, "capabilities":[], "detail":"Collector integration is not configured."}

@app.post("/api/v1/collector/heartbeat", dependencies=[Depends(require_ingest_auth)])
def heartbeat(payload: dict):
    return {"accepted": True, "verified_live": False, "detail":"Heartbeat alone does not verify telemetry capture."}

@app.post("/api/v1/ingest/events", dependencies=[Depends(require_ingest_auth)])
def ingest(batch: IngestBatch):
    existing = {e["id"] for e in EVENTS}
    accepted = 0
    for event in batch.events:
        row = event.model_dump(mode="json")
        if row["id"] not in existing:
            EVENTS.append(row); existing.add(row["id"]); accepted += 1
    return {"accepted":accepted, "duplicates":len(batch.events)-accepted}

@app.get("/api/v1/overview")
def overview():
    events = EVENTS if MODE == "demo" else [e for e in EVENTS if e.get("provenance") != "demo"]
    return {"mode":MODE, "provenance":MODE, "event_count":len(events), "device_count":len({e.get("source_ip") for e in events if e.get("source_ip")}), "alerts_open":sum(a["status"]=="open" for a in ALERTS) if MODE=="demo" else 0, "inbound_bytes":None, "outbound_bytes":None, "throughput_bps":None, "telemetry_available":bool(events), "events":events[-8:], "alerts":ALERTS if MODE=="demo" else []}

@app.get("/api/v1/events")
def events(q: str = "", event_type: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    rows = EVENTS if MODE == "demo" else [e for e in EVENTS if e.get("provenance") != "demo"]
    if q: rows = [e for e in rows if q.casefold() in str(e).casefold()]
    if event_type: rows = [e for e in rows if e.get("event_type")==event_type]
    total=len(rows); start=(page-1)*page_size
    return {"items":rows[start:start+page_size], "page":page, "page_size":page_size, "total":total, "provenance":"demo" if MODE=="demo" else MODE}

@app.get("/api/v1/devices")
def devices():
    if MODE != "demo": return {"items":[], "provenance":MODE}
    items=[]
    for idx, ip in enumerate(["192.0.2.10","192.0.2.11","192.0.2.12"]):
        items.append({"device_id":f"demo-device-{idx+1}","ip":ip,"label":["Workstation","Media device","Laptop"][idx],"first_observed":EVENTS[idx*2]["timestamp"],"last_observed":EVENTS[idx*2+1]["timestamp"],"source":"demo fixture","identity_confidence":"fictional"})
    return {"items":items,"provenance":"demo"}

@app.get("/api/v1/domains")
def domains():
    rows=[e for e in EVENTS if e.get("domain") and (MODE=="demo" or e.get("provenance")!="demo")]
    return {"items":rows,"provenance":"demo" if MODE=="demo" else MODE,"note":"A DNS observation is not evidence of a successful website visit."}

@app.get("/api/v1/traffic/timeseries")
def timeseries(range: str = Query("1h", pattern="^(5m|15m|1h|24h)$")):
    if MODE != "demo": return {"items":[],"available":False,"reason":"No verified telemetry."}
    return {"items":[{"timestamp":e["timestamp"],"bytes":e["bytes"],"event_type":e["event_type"],"provenance":"demo"} for e in EVENTS],"available":True,"provenance":"demo","range":range}

@app.get("/api/v1/traffic/protocols")
def protocols():
    counts={}
    for e in EVENTS:
        if MODE=="demo" or e.get("provenance")!="demo": counts[e.get("protocol") or "Unknown"]=counts.get(e.get("protocol") or "Unknown",0)+1
    return {"items":[{"protocol":k,"count":v} for k,v in counts.items()],"available":bool(counts),"provenance":"demo" if MODE=="demo" else MODE}

@app.get("/api/v1/alerts")
def alerts(status: str | None=None):
    return {"items":[a for a in ALERTS if not status or a["status"]==status],"provenance":"demo" if MODE=="demo" else MODE}

@app.patch("/api/v1/alerts/{alert_id}")
def patch_alert(alert_id: str, payload: dict):
    alert=next((a for a in ALERTS if a["id"]==alert_id),None)
    if not alert: raise HTTPException(404,"Alert not found.")
    if payload.get("status") not in {"open","acknowledged","investigating","resolved","false_positive"}: raise HTTPException(422,"Invalid alert status.")
    alert["status"]=payload["status"]
    return alert

@app.get("/api/v1/rules")
def rules():
    return {"items":[],"status":"not_configured","note":"No detection rules are currently evaluating imported or live events."}

@app.get("/api/v1/audit")
def audit(): return {"items":[]}

@app.get("/api/v1/export/events")
def export_events(q: str=""):
    rows=[e for e in EVENTS if (MODE=="demo" or e.get("provenance")!="demo") and (not q or q.casefold() in str(e).casefold())]
    buf=io.StringIO(); writer=csv.DictWriter(buf,fieldnames=["id","timestamp","event_type","source_ip","destination_ip","protocol","bytes","domain","source","provenance"]); writer.writeheader()
    for row in rows:
        safe={k:v for k,v in row.items() if k in writer.fieldnames}
        for key,value in safe.items():
            if isinstance(value,str) and value.startswith(("=","+","-","@","\t","\r")): safe[key]="'"+value
        writer.writerow(safe)
    return Response(buf.getvalue(),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=netwatch-events.csv","X-Export-Count":str(len(rows))})
