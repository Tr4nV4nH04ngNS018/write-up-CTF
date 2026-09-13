$events = Get-WinEvent -Path 'triage\Application.evtx' | Where-Object { $_.TimeCreated.ToString('yyyy-MM-dd') -eq '2026-08-19' }
$results = @()
foreach ($e in $events) {
    $results += [PSCustomObject]@{
        Time = $e.TimeCreated.ToString('HH:mm:ss')
        Provider = $e.ProviderName
        Id = $e.Id
        Level = $e.LevelDisplayName
        Message = ($e.Message -replace '\r?\n', ' ')
    }
}
$results | Sort-Object Time | Export-Csv -Path 'application_events.csv' -NoTypeInformation -Encoding utf8
Write-Host "Exported $($results.Count) events to application_events.csv"
