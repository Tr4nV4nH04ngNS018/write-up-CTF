import os
import shutil

root = r"c:\Users\ACER\Downloads\ctf\ctf pwnsec"

# 1. Remove 4.27 GB memory dump
dmp_file = os.path.join(root, "KUVEE-20260819-061315.dmp")
if os.path.exists(dmp_file):
    os.remove(dmp_file)
    print("Removed KUVEE-20260819-061315.dmp")

# 2. Challenge folders
pickle_dir = os.path.join(root, "challenge", "pickle")
hunting_dir = os.path.join(root, "challenge", "hunting_01")
os.makedirs(pickle_dir, exist_ok=True)
os.makedirs(hunting_dir, exist_ok=True)

# Move pickle files
pickle_files = ["Dockerfile", "flag.txt", "sessionstore.py", "webapp.py", "static", "templates"]
for pf in pickle_files:
    src = os.path.join(root, "challenge", pf)
    dst = os.path.join(pickle_dir, pf)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {pf} -> challenge/pickle/")

dc_src = os.path.join(root, "docker-compose.yml")
if os.path.exists(dc_src):
    shutil.move(dc_src, os.path.join(pickle_dir, "docker-compose.yml"))
    print("Moved docker-compose.yml -> challenge/pickle/")

pycache = os.path.join(root, "challenge", "__pycache__")
if os.path.exists(pycache):
    shutil.rmtree(pycache)

# Move hunting files
for hf in ["artefact.zip", "2026-08-19T053959_disk.zip"]:
    src = os.path.join(root, hf)
    if os.path.exists(src):
        shutil.move(src, os.path.join(hunting_dir, hf))
        print(f"Moved {hf} -> challenge/hunting_01/")

# 3. Scripts into scripts_dev
scripts_dir = os.path.join(root, "scripts_dev")
for s in ["dump_history.py", "extract_debug.py", "search_kape.py"]:
    src = os.path.join(root, s)
    if os.path.exists(src):
        shutil.move(src, os.path.join(scripts_dir, s))
        print(f"Moved {s} -> scripts_dev/")

# 4. Analysis files into triage
triage_dir = os.path.join(root, "triage")
os.makedirs(triage_dir, exist_ok=True)
for a in ["application_events.csv", "edge_history.txt", "kape_files.txt", "prefetch_timeline_20260819.txt", "security_4688.csv", "wmi_events.csv"]:
    src = os.path.join(root, a)
    if os.path.exists(src):
        shutil.move(src, os.path.join(triage_dir, a))
        print(f"Moved {a} -> triage/")

print("Cleanup complete!")
