[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

function Invoke-AtlasStep([string]$Description, [scriptblock]$Action) {
    Write-Host "[atlas] $Description"
    if (-not $DryRun) { & $Action }
}

Invoke-AtlasStep "Creating local environment file" {
    $source = Join-Path $root ".env.example"
    $target = Join-Path $root ".env"
    if (-not (Test-Path $target)) { Copy-Item $source $target }
}
Write-Host "[atlas] Bootstrap complete. Review .env before starting Docker Compose."
