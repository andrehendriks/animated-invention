[CmdletBinding()]
param(
  [int]$LocalPort = 18081,
  [string]$Namespace = "atlas",
  [string]$Service = "atlas-frontend",
  [int]$ServicePort = 8081,
  [string]$KubectlPath
)

$ErrorActionPreference = "Stop"
$localApplicationData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
$logDirectory = Join-Path $localApplicationData "ProjectAtlas\logs"
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$logFile = Join-Path $logDirectory "frontend-port-forward.log"
trap {
  Add-Content -Path $logFile -Value "$(Get-Date -Format o) Port-forward failed: $($_.Exception.Message)"
  exit 1
}
if (-not $KubectlPath) {
  $KubectlPath = (Get-Command kubectl.exe -ErrorAction Stop).Source
}
$listeners = @(Get-NetTCPConnection -State Listen -LocalPort $LocalPort -ErrorAction SilentlyContinue)
if ($listeners.Count -gt 0) {
  $portForwardProcess = $listeners | ForEach-Object {
    Get-CimInstance Win32_Process -Filter "ProcessId = $($_.OwningProcess)"
  } | Where-Object {
    $_.Name -eq "kubectl.exe" -and $_.CommandLine -match "port-forward.+service/$Service.+$LocalPort`:$ServicePort"
  }

  if ($portForwardProcess) {
    Add-Content -Path $logFile -Value "$(Get-Date -Format o) An Atlas frontend port-forward already owns port $LocalPort."
    exit 0
  }

  throw "Local port $LocalPort is already used by another process."
}

Add-Content -Path $logFile -Value "$(Get-Date -Format o) Starting Atlas frontend port-forward on port $LocalPort."
& $KubectlPath port-forward --namespace $Namespace "service/$Service" "${LocalPort}:${ServicePort}" 2>&1 |
  ForEach-Object { Add-Content -Path $logFile -Value $_ }
exit $LASTEXITCODE
