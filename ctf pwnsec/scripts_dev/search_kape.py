with open('kape_files.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f]

def search_patterns(patterns):
    for p in patterns:
        matches = [l for l in lines if p.lower() in l.lower()]
        print(f"=== Matches for '{p}' ({len(matches)}) ===")
        for m in matches[:15]:
            print(" ", m)

search_patterns(['Kuvee', 'Downloads', 'History', 'ConsoleHost', 'Prefetch', 'FireAnt'])
