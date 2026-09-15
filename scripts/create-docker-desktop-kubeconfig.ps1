[CmdletBinding()]
param(
  [string]$SourcePath = $(if ($env:KUBECONFIG) { $env:KUBECONFIG } else { Join-Path $HOME ".kube\config" }),
  [string]$OutputPath = ".atlas\kubeconfig"
)

$ErrorActionPreference = "Stop"
$source = Resolve-Path -LiteralPath $SourcePath -ErrorAction Stop
$sourceServer = & kubectl --kubeconfig $source.Path config view --minify -o jsonpath='{.clusters[0].cluster.server}'
if ($LASTEXITCODE -ne 0 -or -not $sourceServer) {
  throw "Could not read the active Kubernetes API server from $($source.Path)."
}
$clusterName = & kubectl --kubeconfig $source.Path config view --minify -o jsonpath='{.contexts[0].context.cluster}'
if ($LASTEXITCODE -ne 0 -or -not $clusterName) {
  throw "Could not read the active Kubernetes cluster name from $($source.Path)."
}

$sourceUri = [Uri]$sourceServer
if (-not $sourceUri.IsLoopback) {
  throw "The active Kubernetes API server is not a loopback address: $sourceServer"
}

$containerServer = "$($sourceUri.Scheme)://host.docker.internal`:$($sourceUri.Port)$($sourceUri.PathAndQuery)"
$config = & kubectl --kubeconfig $source.Path config view --raw --flatten
if ($LASTEXITCODE -ne 0 -or -not $config) {
  throw "Could not flatten kubeconfig $($source.Path)."
}

$output = [IO.Path]::GetFullPath($OutputPath)
New-Item -ItemType Directory -Force (Split-Path -Parent $output) | Out-Null
Set-Content -LiteralPath $output -Value ($config -join [Environment]::NewLine)
& kubectl --kubeconfig $output config set-cluster $clusterName --server=$containerServer --tls-server-name=kubernetes | Out-Null
if ($LASTEXITCODE -ne 0) {
  throw "Could not set the container Kubernetes API server in $output."
}
Write-Output "Created container kubeconfig: $output"
Write-Output "Set ATLAS_KUBECONFIG_PATH=$output in .env and recreate the backend."
