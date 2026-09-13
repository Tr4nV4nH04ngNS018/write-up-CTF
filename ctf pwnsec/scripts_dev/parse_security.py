import xml.etree.ElementTree as ET
import Evtx.Evtx as evtx

evtx_path = r"triage\C\Windows\System32\winevt\logs\Security.evtx"

events_4688 = []
with evtx.Evtx(evtx_path) as log:
    for record in log.records():
        xml_content = record.xml()
        if '4688' not in xml_content and '4697' not in xml_content and '7045' not in xml_content:
            continue
        root = ET.fromstring(xml_content)
        ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
        eid_elem = root.find('.//ns:EventID', ns)
        if eid_elem is None:
            continue
        eid = eid_elem.text
        if eid in ['4688', '4697']:
            time_elem = root.find('.//ns:TimeCreated', ns)
            time_str = time_elem.attrib.get('SystemTime', '') if time_elem is not None else ''
            if '2026-08-19' in time_str:
                data_elements = root.findall('.//ns:EventData/ns:Data', ns)
                data = {d.attrib.get('Name', f'arg_{i}'): d.text for i, d in enumerate(data_elements)}
                events_4688.append((time_str, eid, data))

events_4688.sort(key=lambda x: x[0])
print(f"Found {len(events_4688)} events on 2026-08-19")
with open("security_4688_20260819.txt", "w", encoding="utf-8") as out:
    for t, eid, data in events_4688:
        out.write(f"[{t}] EventID: {eid}\n")
        for k, v in data.items():
            if v:
                out.write(f"  {k}: {v}\n")
        out.write("-" * 50 + "\n")

print("Saved to security_4688_20260819.txt")
