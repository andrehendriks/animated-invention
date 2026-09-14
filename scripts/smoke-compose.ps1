[CmdletBinding()]
param(
  [int]$BackendPort = 18000,
  [int]$FrontendPort = 18080,
  [int]$PrometheusPort = 19090,
  [int]$GrafanaPort = 13000,
  [int]$TimeoutSeconds = 240,
  [switch]$Authentication
)

$ErrorActionPreference = "Stop"
$curlCommand = Get-Command curl.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $curlCommand) {
  $curlCommand = Get-Command curl -CommandType Application -ErrorAction Stop | Select-Object -First 1
}

function Invoke-AtlasCompose {
  param(
    [Parameter(Mandatory)]
    [string[]]$Arguments,
    [switch]$DisplayOutput
  )

  $composeFile = Join-Path (Get-Location).ProviderPath "docker-compose.yml"
  $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
  $startInfo.FileName = "docker"
  $startInfo.WorkingDirectory = [System.IO.Path]::GetTempPath()
  $startInfo.UseShellExecute = $false
  $startInfo.RedirectStandardOutput = $true
  $startInfo.RedirectStandardError = $true
  $startInfo.Arguments = "compose -f `"$composeFile`" $($Arguments -join ' ')"

  $process = [System.Diagnostics.Process]::new()
  $process.StartInfo = $startInfo
  [void]$process.Start()
  $outputTask = $process.StandardOutput.ReadToEndAsync()
  $errorTask = $process.StandardError.ReadToEndAsync()
  $process.WaitForExit()
  $output = $outputTask.GetAwaiter().GetResult()
  $error = $errorTask.GetAwaiter().GetResult()

  if ($DisplayOutput) {
    if ($output) {
      Write-Host $output -NoNewline
    }
    if ($error) {
      Write-Host $error -NoNewline
    }
  }

  if ($process.ExitCode -ne 0) {
    $details = "$output$error".Trim()
    throw "docker compose failed with exit code $($process.ExitCode): $details"
  }

  if (-not $DisplayOutput -and $output) {
    Write-Output $output
  }
}

$env:ATLAS_BACKEND_PORT = $BackendPort
$env:ATLAS_FRONTEND_PORT = $FrontendPort
$env:ATLAS_PROMETHEUS_PORT = $PrometheusPort
$env:ATLAS_GRAFANA_PORT = $GrafanaPort
$projectName = "atlas-smoke-$PID"
$grafanaUser = "atlas-smoke"
$grafanaPassword = "atlas-smoke-test-password"
$env:ATLAS_GRAFANA_ADMIN_USER = $grafanaUser
$env:ATLAS_GRAFANA_ADMIN_PASSWORD = $grafanaPassword
$apiKeyHeader = @()
if ($Authentication) {
  $env:ATLAS_AUTH_ENABLED = "true"
  $env:ATLAS_API_KEY = "atlas-smoke-api-key"
  $apiKeyHeader = @("--header", "X-API-Key: $env:ATLAS_API_KEY")
} else {
  $env:ATLAS_AUTH_ENABLED = "false"
  $env:ATLAS_API_KEY = ""
}
$started = $false

try {
  $started = $true
  Invoke-AtlasCompose -Arguments @("-p", $projectName, "up", "-d", "--build") -DisplayOutput

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  $ready = $false
  do {
    $servicesOutput = Invoke-AtlasCompose -Arguments @("-p", $projectName, "ps", "--format", "json")
    $services = @($servicesOutput -split "\r?\n" | Where-Object { $_ } | ConvertFrom-Json)
    $healthCheckedServices = @("ollama", "backend", "frontend", "grafana")
    $unhealthyServices = @($healthCheckedServices | Where-Object {
      $service = $services | Where-Object Service -eq $_
      -not $service -or $service.Health -ne "healthy"
    })
    $prometheus = $services | Where-Object Service -eq "prometheus"
    $ready = $services.Count -eq 5 -and $unhealthyServices.Count -eq 0 -and $prometheus.State -eq "running"

    if (-not $ready) {
      Start-Sleep -Seconds 5
    }
  } while (-not $ready -and (Get-Date) -lt $deadline)

  if (-not $ready) {
    Invoke-AtlasCompose -Arguments @("-p", $projectName, "ps") -DisplayOutput
    throw "Compose services did not reach the expected runtime state within $TimeoutSeconds seconds."
  }

  $page = & $curlCommand.Path --fail --silent "http://localhost:$FrontendPort/"
  $health = & $curlCommand.Path --fail --silent "http://localhost:$FrontendPort/api/health" | ConvertFrom-Json
  $protectedRouteStatus = "200"
  if ($Authentication) {
    $responseFile = [IO.Path]::GetTempFileName()
    try {
      $protectedRouteStatus = & $curlCommand.Path --silent --output $responseFile --write-out "%{http_code}" "http://localhost:$FrontendPort/api/docker/containers"
    } finally {
      Remove-Item $responseFile -Force
    }
  }
  $containers = & $curlCommand.Path --fail --silent @apiKeyHeader "http://localhost:$FrontendPort/api/docker/containers"
  $targets = & $curlCommand.Path --fail --silent "http://localhost:$PrometheusPort/api/v1/targets" | ConvertFrom-Json
  $rules = & $curlCommand.Path --fail --silent "http://localhost:$PrometheusPort/api/v1/rules" | ConvertFrom-Json
  $dashboard = & $curlCommand.Path --fail --silent --user "${grafanaUser}:${grafanaPassword}" "http://localhost:$GrafanaPort/api/dashboards/uid/atlas-overview" | ConvertFrom-Json
  $hasApplicationRoot = [regex]::IsMatch([string]$page, [regex]::Escape('<div id="root"></div>'))
  $hasHealthyProxy = $health.status -eq "ok"
  $hasAuthenticationBoundary = -not $Authentication -or $protectedRouteStatus -eq "401"
  $hasAtlasPrometheusTarget = @($targets.data.activeTargets | Where-Object {
    $_.labels.job -eq "atlas-backend" -and $_.health -eq "up"
  }).Count -eq 1
  $ruleNames = @($rules.data.groups.rules | ForEach-Object name)
  $hasAtlasAlertRules = $ruleNames -contains "AtlasBackendDown" -and $ruleNames -contains "AtlasBackendHighMemory"
  $hasAtlasGrafanaDashboard = $dashboard.dashboard.uid -eq "atlas-overview"
  $hasContainerInventory = $false
  try {
    $null = ConvertFrom-Json -InputObject $containers -ErrorAction Stop
    $hasContainerInventory = $true
  } catch {
    $hasContainerInventory = $false
  }
  if (-not ($hasApplicationRoot -and $hasHealthyProxy -and $hasAuthenticationBoundary -and $hasContainerInventory -and $hasAtlasPrometheusTarget -and $hasAtlasAlertRules -and $hasAtlasGrafanaDashboard)) {
    throw "Frontend, proxied health, API-key boundary, Docker inventory, Prometheus target or alert rules, or Grafana dashboard response did not match its expected contract."
  }

  Write-Output "Compose smoke test passed."
} finally {
  if ($started) {
    Invoke-AtlasCompose -Arguments @("-p", $projectName, "down", "--volumes", "--remove-orphans") -DisplayOutput
  }
}
