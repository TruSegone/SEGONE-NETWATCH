$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Test-Path '.venv\Scripts\python.exe')) { throw 'Run .\scripts\setup-windows.ps1 first.' }
foreach ($port in @(8000,5173)) {
  if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) { throw "Port $port already has a listener; stop it before starting NetWatch." }
}
$backend = Start-Process -FilePath (Join-Path $root '.venv\Scripts\python.exe') -ArgumentList '-m','uvicorn','app.main:app','--app-dir','backend','--host','127.0.0.1','--port','8000' -WorkingDirectory $root -PassThru -WindowStyle Hidden
$frontend = Start-Process -FilePath 'node.exe' -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1' -WorkingDirectory (Join-Path $root 'frontend') -PassThru -WindowStyle Hidden
Set-Content -LiteralPath (Join-Path $root '.netwatch-processes.json') -Value (@{backend=$backend.Id;frontend=$frontend.Id}|ConvertTo-Json)
Write-Host "Backend PID $($backend.Id): http://127.0.0.1:8000/docs"
Write-Host "Frontend PID $($frontend.Id): http://127.0.0.1:5173"
Write-Host 'Stop with .\scripts\stop-dev.ps1'
