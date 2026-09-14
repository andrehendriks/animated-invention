[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$taskName = "Project Atlas frontend port-forward"
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Output "Removed scheduled task '$taskName'."
