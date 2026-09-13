$events = Get-WinEvent -Path 'triage\Microsoft-Windows-WMI-Activity%4Operational.evtx'
$results = foreach ($e in $events) {
    $xml = [xml]$e.ToXml()
    $data = @{}
    foreach ($d in $xml.Event.UserData.FirstChild.ChildNodes) {
        $data[$d.LocalName] = $d.InnerText
    }
    [PSCustomObject]@{
        Time = $e.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss")
        Id = $e.Id
        Operation = $data['Operation']
        User = $data['User']
        ClientProcessId = $data['ClientProcessId']
        GroupOperationId = $data['GroupOperationId']
        NamespaceName = $data['NamespaceName']
    }
}
$results | Sort-Object Time | Export-Csv -Path 'wmi_events.csv' -NoTypeInformation -Encoding utf8
Write-Host "Exported $($results.Count) events to wmi_events.csv"
