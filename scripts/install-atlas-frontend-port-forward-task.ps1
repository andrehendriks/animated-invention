[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$taskName = "Project Atlas frontend port-forward"
$localApplicationData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
$installedScriptDirectory = Join-Path $localApplicationData "ProjectAtlas\scripts"
New-Item -ItemType Directory -Path $installedScriptDirectory -Force | Out-Null
$scriptPath = Join-Path $installedScriptDirectory "start-atlas-frontend-port-forward.ps1"
Copy-Item -Path (Join-Path $PSScriptRoot "start-atlas-frontend-port-forward.ps1") -Destination $scriptPath -Force
$kubectlPath = (Get-Command kubectl.exe -ErrorAction Stop).Source
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$forwardArguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$scriptPath`" -KubectlPath `"$kubectlPath`""
$encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes(
  "Start-Process -FilePath 'powershell.exe' -ArgumentList '$forwardArguments' -WindowStyle Hidden"
))

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -EncodedCommand $encodedCommand"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$principal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)

Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Provides local Atlas frontend access through kubectl port-forward." -Force -ErrorAction Stop | Out-Null
Start-ScheduledTask -TaskName $taskName -ErrorAction Stop
Write-Output "Installed and started scheduled task '$taskName'."
