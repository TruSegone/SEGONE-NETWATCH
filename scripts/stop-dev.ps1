$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$state = Join-Path $root '.netwatch-processes.json'
if (Test-Path -LiteralPath $state) {
  $pids = Get-Content -LiteralPath $state -Raw | ConvertFrom-Json
  $roots = @([int]$pids.backend,[int]$pids.frontend) | Where-Object { $_ -gt 0 }
  $all = [System.Collections.Generic.List[int]]::new()
  foreach ($id in $roots) { $all.Add($id) }
  $processes = @(Get-CimInstance Win32_Process)
  $changed = $true
  while ($changed) {
    $changed = $false
    foreach ($process in $processes) {
      if ($all.Contains([int]$process.ParentProcessId) -and -not $all.Contains([int]$process.ProcessId)) {
        $all.Add([int]$process.ProcessId); $changed = $true
      }
    }
  }
  $descendants = @($all | Select-Object -Skip $roots.Count)
  [array]::Reverse($descendants)
  foreach ($id in (@($descendants) + $roots)) {
    if (Get-Process -Id $id -ErrorAction SilentlyContinue) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
  }
  Remove-Item -LiteralPath $state
}
Write-Host 'SEGONE NetWatch development processes stopped.'
