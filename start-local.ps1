$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$localRoot = Join-Path $projectRoot '.local'
Set-Location $projectRoot
function Invoke-Checked([scriptblock]$Command) {
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "Local setup command failed (exit $LASTEXITCODE). See .local logs." }
}
function Test-OwnedProcess($Record) {
    if (-not $Record) { return $false }
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($Record.Id)" -ErrorAction SilentlyContinue
    return $process -and $process.CommandLine.Contains((Join-Path $projectRoot 'scripts/local_process.ps1')) -and ([string]$process.CreationDate.ToUniversalTime().Ticks -eq [string]$Record.CreatedTicks)
}
function Wait-Http([string]$Url) {
    for ($attempt=0; $attempt -lt 60; $attempt++) {
        try { $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3; if ($response.StatusCode -eq 200) { return } } catch { }
        Start-Sleep -Seconds 1
    }
    throw "Not ready: $Url. Inspect .local/*.log; no unrelated process was stopped."
}
$pgBin = Split-Path -Parent (Get-Command pg_ctl.exe -ErrorAction Stop).Source
Invoke-Checked { python scripts/local_environment.py prepare }
$localConfig = Get-Content -LiteralPath (Join-Path $localRoot 'environment.json') -Raw | ConvertFrom-Json
foreach ($entry in $localConfig.PSObject.Properties) { [Environment]::SetEnvironmentVariable($entry.Name, [string]$entry.Value, 'Process') }
$pgData = Join-Path $localRoot 'postgres'
if (-not (Test-Path -LiteralPath (Join-Path $pgData 'PG_VERSION'))) {
    Invoke-Checked { & (Join-Path $pgBin 'initdb.exe') -D $pgData -U ratchethub_bootstrap "--pwfile=$(Join-Path $localRoot 'initdb-password')" --auth=scram-sha-256 --encoding=UTF8 --locale=C *> (Join-Path $localRoot 'initdb.log') }
}
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData status *> $null
if ($LASTEXITCODE -ne 0) {
    if (Get-NetTCPConnection -LocalPort 55432 -State Listen -ErrorAction SilentlyContinue) { throw 'Port 55432 is occupied by an unrelated service; refusing to reuse it.' }
    Invoke-Checked { & (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -l (Join-Path $localRoot 'postgres.log') -o '-h 127.0.0.1 -p 55432' -w start }
}
Invoke-Checked { python scripts/local_environment.py database }
Push-Location (Join-Path $projectRoot 'apps/api')
try {
    $migration = Start-Process -FilePath (Get-Command python.exe).Source -ArgumentList @('-m','alembic','upgrade','head') -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -RedirectStandardOutput (Join-Path $localRoot 'migrations.stdout.log') -RedirectStandardError (Join-Path $localRoot 'migrations.stderr.log') -Wait -PassThru
    if ($migration.ExitCode -ne 0) { throw 'Existing migrations failed on the isolated database. See .local/migrations.stderr.log.' }
} finally { Pop-Location }
$statePath = Join-Path $localRoot 'processes.json'
$state = @{}
if (Test-Path -LiteralPath $statePath) {
    $saved = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    foreach ($entry in $saved.PSObject.Properties) { $state[$entry.Name] = $entry.Value }
}
foreach ($service in @('api','web')) {
    if (Test-OwnedProcess $state[$service]) { continue }
    $port = if ($service -eq 'api') { 8003 } else { 3003 }
    if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) { throw "Port $port is occupied by an unrelated service; refusing to reuse it." }
    $wrapper = Join-Path $projectRoot 'scripts/local_process.ps1'
    $process = Start-Process -FilePath (Get-Command powershell.exe).Source -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$wrapper`"",'-Service',$service) -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $localRoot "$service.stdout.log") -RedirectStandardError (Join-Path $localRoot "$service.stderr.log") -PassThru
    $actual = Get-CimInstance Win32_Process -Filter "ProcessId=$($process.Id)"
    $state[$service] = @{ Id=$process.Id; CreatedTicks=[string]$actual.CreationDate.ToUniversalTime().Ticks }
    $state | ConvertTo-Json | Set-Content -LiteralPath $statePath
}
Wait-Http 'http://127.0.0.1:8003/health'
Wait-Http 'http://127.0.0.1:3003/'
Invoke-Checked { python scripts/create_local_account.py }
Write-Host 'Frontend: http://127.0.0.1:3003'
Write-Host 'API:      http://127.0.0.1:8003/docs'
Write-Host 'Database: isolated project-local PostgreSQL on 127.0.0.1:55432'
Write-Host 'Offline heuristic AI; fake SMS/voice/email. No Redis required for memory queues.'
