import sqlite3

conn = sqlite3.connect(r'triage\C\Users\kuveeeee\AppData\Local\Microsoft\Edge\User Data\Default\History')
c = conn.cursor()

with open('edge_history.txt', 'w', encoding='utf-8') as out:
    out.write('=== URLS ===\n')
    for row in c.execute("SELECT datetime(last_visit_time/1000000-11644473600, 'unixepoch'), url, title FROM urls ORDER BY last_visit_time ASC"):
        out.write(f"{row[0]} | {row[1]} | {row[2]}\n")

    out.write('\n=== DOWNLOADS ===\n')
    for row in c.execute("SELECT datetime(start_time/1000000-11644473600, 'unixepoch'), target_path, tab_url, tab_referrer_url FROM downloads ORDER BY start_time ASC"):
        out.write(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}\n")

print('Saved edge_history.txt')
