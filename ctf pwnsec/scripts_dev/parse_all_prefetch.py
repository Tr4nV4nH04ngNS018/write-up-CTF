import os
import glob
import windowsprefetch

pf_files = glob.glob("triage/prefetch/*.pf")
executions = []

for pf_path in pf_files:
    try:
        pf = windowsprefetch.Prefetch(pf_path)
        exe = pf.executableName
        count = pf.runCount
        for ts in pf.timestamps:
            if ts and ts.startswith("2026-08-19"):
                executions.append((ts, exe, os.path.basename(pf_path), pf.filenames))
    except Exception as e:
        # print(f"Error parsing {pf_path}: {e}")
        pass

executions.sort(key=lambda x: x[0])

print(f"Total executions on 2026-08-19: {len(executions)}")
with open("prefetch_timeline_20260819.txt", "w", encoding="utf-8") as f:
    for ts, exe, pf_name, files in executions:
        f.write(f"[{ts}] {exe} ({pf_name})\n")

print("Saved timeline to prefetch_timeline_20260819.txt")
