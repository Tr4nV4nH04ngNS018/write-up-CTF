import csv

with open('application_events.csv', mode='r', encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    for row in r:
        t = row['Time']
        if '11:45:' <= t <= '12:10:00':
            print(f"[{row['Time']}] {row['Provider']} ({row['Id']}): {row['Message'][:120]}")
