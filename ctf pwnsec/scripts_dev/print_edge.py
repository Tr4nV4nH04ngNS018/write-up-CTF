with open('edge_history.txt', 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        if '2026-08-19' in line or 'DOWNLOAD' in line:
            clean = line.strip().encode('ascii', 'ignore').decode('ascii')
            print(clean[:150])
