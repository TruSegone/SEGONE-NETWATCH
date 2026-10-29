# Troubleshooting

- Check Python: `python --version`; check Node: `node --version`.
- Start backend manually: `..venvScriptspython.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000`.
- Start frontend manually: `cd frontend; npm run dev`.
- If dashboard reports API offline, check `/api/v1/health` and confirm port 8000 is free.
- If ingestion returns 503, set `NETWATCH_INGEST_TOKEN` in the backend process environment and restart it.
- No collector/capture backend is included in this milestone; unavailable collector status is expected.
