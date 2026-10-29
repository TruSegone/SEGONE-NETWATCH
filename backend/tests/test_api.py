import asyncio
import httpx
import pytest
from pydantic import ValidationError
from app.main import IngestEvent, app

async def request(method, path, **kwargs):
    transport=httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,base_url="http://test") as client:
        return await client.request(method,path,**kwargs)

def get(path, **kwargs): return asyncio.run(request("GET",path,**kwargs))
def post(path, **kwargs): return asyncio.run(request("POST",path,**kwargs))

def test_health_separates_collector_from_api():
    response=get("/api/v1/health")
    assert response.status_code==200
    assert response.json()["application"]=="healthy"
    assert response.json()["collector"]=="unverified"

def test_demo_provenance_and_dns_caveat():
    assert get("/api/v1/overview").json()["provenance"]=="demo"
    assert "not evidence" in get("/api/v1/domains").json()["note"]

def test_ingestion_disabled_without_token():
    assert post("/api/v1/ingest/events",json={"events":[]}).status_code==503

def test_events_pagination():
    result=get("/api/v1/events?page=1&page_size=2").json()
    assert len(result["items"])==2 and result["total"]>=2

def test_csv_export_is_explicitly_provenanced():
    response=get("/api/v1/export/events")
    assert "provenance" in response.text.splitlines()[0]

def test_unverified_live_provenance_is_rejected():
    with pytest.raises(ValidationError):
        IngestEvent.model_validate({"id":"x","timestamp":"2026-01-01T00:00:00Z","event_type":"connection","source":"collector","provenance":"live"})
