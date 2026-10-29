# Architecture

The React/TypeScript/Vite frontend calls the independent FastAPI service over loopback HTTP. The backend owns the versioned API, deterministic seeded demo fixtures, limited event ingestion validation, alert state, and CSV export. The ingestion endpoint requires a bearer token and is disabled unless `NETWATCH_INGEST_TOKEN` is set. A supplied heartbeat explicitly does not prove packet capture.

This milestone keeps demo records in process memory, so reset is achieved by restarting the API. There is not yet a persistent database, migration chain, separate collector process, normalization pipeline, detection engine, or source adapter. This is an honest foundation, not a production-ready monitoring system.
