# Windows 11 setup

Install Python 3.12 or newer, Node.js 20.19+ or 22.12+, and Git. Open PowerShell in the checkout. If local policy blocks project scripts, use a process-scoped policy for this terminal only: `Set-ExecutionPolicy -Scope Process Bypass`.

```powershell
.\scripts\setup-windows.ps1
.\scripts\start-dev.ps1
```

Frontend: http://127.0.0.1:5173. API/OpenAPI: http://127.0.0.1:8000/docs. Stop via `.scriptsstop-dev.ps1` or close the processes. Backend and frontend run as the current user; neither requires administrator privileges. Live capture is not included, so no capture driver or elevation is needed for this release.

To test collector ingestion locally, generate a private token and set `NETWATCH_INGEST_TOKEN` in the backend environment before starting it. Do not commit the token. Confirm application health at `/api/v1/health`; this does not confirm collection. Current collector status is deliberately `unavailable`.
