$events = Get-WinEvent -Path 'triage\C\Windows\System32\winevt\logs\System.evtx' | Where-Object { $_.TimeCreated.ToString('yyyy-MM-dd') -eq '2026-08-19' }
$usb = $events | Where-Object { $_.Message -match 'USB|disk|volume|Kingston|Removable' }
Write-Host "Found $($usb.Count) USB/disk events"
foreach ($u in ($usb | Select-Object -First 30)) {
    Write-Host "$($u.TimeCreated.ToString('HH:mm:ss')) $($u.Id) $($u.ProviderName): $($u.Message -replace '\r?\n', ' ')"
}
