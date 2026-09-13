import xml.etree.ElementTree as ET
import Evtx.Evtx as evtx

evtx_path = r"triage\C\Windows\System32\winevt\logs\Microsoft-Windows-Windows Defender%4Operational.evtx"

with evtx.Evtx(evtx_path) as log:
    for record in log.records():
        xml_content = record.xml()
        root = ET.fromstring(xml_content)
        # remove namespace
        ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
        eid = root.find('.//ns:EventID', ns)
        time_created = root.find('.//ns:TimeCreated', ns)
        eid_str = eid.text if eid is not None else "Unknown"
        time_str = time_created.attrib.get('SystemTime', '') if time_created is not None else ""
        
        # print all event data
        data_elements = root.findall('.//ns:EventData/ns:Data', ns)
        data_dict = {d.attrib.get('Name', f'arg_{i}'): d.text for i, d in enumerate(data_elements)}
        
        print(f"[{time_str}] EventID: {eid_str}")
        for k, v in data_dict.items():
            if v:
                print(f"  {k}: {v}")
        print("-" * 50)
