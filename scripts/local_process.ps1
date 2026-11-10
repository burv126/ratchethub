param([Parameter(Mandatory=$true)][ValidateSet('api','web')][string]$Service)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$localConfig = Get-Content -LiteralPath (Join-Path $projectRoot '.local/environment.json') -Raw | ConvertFrom-Json
foreach ($entry in $localConfig.PSObject.Properties) { [Environment]::SetEnvironmentVariable($entry.Name, [string]$entry.Value, 'Process') }
if ($Service -eq 'api') {
    Set-Location (Join-Path $projectRoot 'apps/api')
    & python -m uvicorn app.main:app --host 127.0.0.1 --port 8003
} else {
    Set-Location (Join-Path $projectRoot 'apps/web')
    & node 'node_modules/next/dist/bin/next' dev --hostname 127.0.0.1 --port 3003
}
exit $LASTEXITCODE
