$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$localRoot = Join-Path $projectRoot '.local'
$statePath = Join-Path $localRoot 'processes.json'
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    foreach ($entry in $state.PSObject.Properties) {
        $record = $entry.Value
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($record.Id)" -ErrorAction SilentlyContinue
        if ($process -and $process.CommandLine.Contains((Join-Path $projectRoot 'scripts/local_process.ps1')) -and ([string]$process.CreationDate.ToUniversalTime().Ticks -eq [string]$record.CreatedTicks)) {
            & taskkill.exe /PID $record.Id /T /F | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "Could not stop owned $($entry.Name) process." }
        }
    }
}
$pgData = Join-Path $localRoot 'postgres'
if (Test-Path -LiteralPath (Join-Path $pgData 'PG_VERSION')) {
    $pgCtl = (Get-Command pg_ctl.exe -ErrorAction Stop).Source
    & $pgCtl -D $pgData status *> $null
    if ($LASTEXITCODE -eq 0) {
        & $pgCtl -D $pgData -m fast -w stop
        if ($LASTEXITCODE -ne 0) { throw 'Could not stop the project-local cluster.' }
    }
}
Write-Host 'Owned local services stopped. Project-local data and credentials retained.'
