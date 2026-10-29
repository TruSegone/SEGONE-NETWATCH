# API

Interactive OpenAPI documentation is available at `/docs` while the API runs. Implemented endpoints include `/api/v1/health`, `/system/status`, `/collector/status`, authenticated `/collector/heartbeat` and `/ingest/events`, `/overview`, `/traffic/timeseries`, `/traffic/protocols`, `/devices`, `/domains`, `/events`, `/alerts`, `/alerts/{alert_id}`, `/rules`, `/audit`, and `/export/events`.

Ingestion accepts up to 500 validated normalized events per request, requires `Authorization: Bearer <NETWATCH_INGEST_TOKEN>`, and rejects requests if no token is configured. Events deduplicate by caller-provided ID. The current in-memory implementation is intended for local development only.
