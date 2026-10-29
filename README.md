# SEGONE NetWatch

Local-first network visibility dashboard for administrators monitoring systems they own or are authorized to manage. Version 0.1 provides a deterministic demo dataset, a real HTTP API, dashboard views, filtered event history, and CSV export. **Live collection is not implemented or verified in this release.** The interface never presents demo records as captured traffic.

## Quick start (Windows 11)

Requirements: Python 3.12+ (Python 3.15 detected in the initial environment), Node.js 20.19+ or 22.12+ (Node 24 detected), npm, and PowerShell. Run from the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& .\scripts\setup-windows.ps1
& .\scripts\start-dev.ps1
```

Open the frontend at http://127.0.0.1:5173 and API docs at http://127.0.0.1:8000/docs. The API binds to loopback. Stop both services with `& .\scripts\stop-dev.ps1`.

## Reviewer website

The public reviewer demo is built in static fixture mode and does not need the local API. GitHub Actions publishes it to https://trusegone.github.io/SEGONE-NETWATCH/ after the Pages workflow succeeds. It contains only fictional demo records and never connects to a monitored network. See [docs/REVIEWER_PREVIEW.md](docs/REVIEWER_PREVIEW.md).

The setup script creates a Python virtual environment and installs dependencies. For collector ingestion, configure a random secret as `NETWATCH_INGEST_TOKEN` in the backend process environment. Ingestion remains disabled without it. Demo mode is selected by default (`NETWATCH_MODE=demo`). Setting another mode does not activate live monitoring; there is no collector or telemetry source in this release.

## Current capabilities

- Demo overview, device inventory, domain observations, traffic event chart, alerts, search, pagination, and CSV export.
- Versioned FastAPI endpoints with request validation, ingestion authentication, deduplication by supplied event ID, and safe CSV formula escaping.
- UI distinguishes application health from collector health and does not substitute demo records after API failure.
- DNS records say “domain observed”; a lookup is not represented as proof of a successful visit.

## Development checks

```powershell
..venv\Scripts\python.exe -m pytest backend\tests
cd frontend; npm test; npm run build
```

## Architecture and limits

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md), [docs/TELEMETRY_SOURCES.md](docs/TELEMETRY_SOURCES.md), [docs/PRIVACY.md](docs/PRIVACY.md), [docs/DETECTION_RULES.md](docs/DETECTION_RULES.md), [docs/API.md](docs/API.md), [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md), and [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

SQLite persistence, migrations, live capture, imported PCAP/log parsers, source setup UI, complete alert audit workflow, and production-hardened multi-user security are not delivered yet. Data in this milestone is held in process memory; restarting resets fixture state. Do not expose this development service to a network. No credentials are committed.
