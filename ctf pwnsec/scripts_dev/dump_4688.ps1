$events = Get-WinEvent -Path 'triage\C\Windows\System32\winevt\logs\Security.evtx' -FilterXPath "*[System[(EventID=4688)]]"
$results = foreach ($e in $events) {
    $xml = [xml]$e.ToXml()
    $data = @{}
    foreach ($d in $xml.Event.EventData.Data) {
        $data[$d.Name] = $d.'#text'
    }
    [PSCustomObject]@{
        Time = $e.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss")
        User = $data['TargetUserName']
        Process = $data['NewProcessName']
        CommandLine = $data['CommandLine']
        Parent = $data['ParentProcessName']
    }
}
$results | Sort-Object Time | Export-Csv -Path 'security_4688.csv' -NoTypeInformation -Encoding utf8
Write-Host "Exported $($results.Count) events to security_4688.csv"
