import os
import shutil
import re

WORKSPACE = r"c:\Users\ACER\Downloads\ctf\ctf pwnsec"

# 1. Create target directories
dirs = [
    os.path.join(WORKSPACE, "writeups"),
    os.path.join(WORKSPACE, "exploits", "pickle"),
    os.path.join(WORKSPACE, "exploits", "phault"),
    os.path.join(WORKSPACE, "exploits", "neon_skies"),
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"[+] Created directory: {d}")

# 2. File relocation mapping
moves = [
    ("WRITEUP.md", os.path.join("writeups", "WRITEUP.md")),
    ("WRITEUP_PICKLE.md", os.path.join("writeups", "WRITEUP_PICKLE.md")),
    ("WRITEUP_PHAULT.md", os.path.join("writeups", "WRITEUP_PHAULT.md")),
    ("WRITEUP_NEON_SKIES.md", os.path.join("writeups", "WRITEUP_NEON_SKIES.md")),
    ("exploit_pickle.py", os.path.join("exploits", "pickle", "exploit_pickle.py")),
    ("exploit_phault.py", os.path.join("exploits", "phault", "exploit_phault.py")),
    ("solve_neon.py", os.path.join("exploits", "neon_skies", "solve_neon.py")),
    ("evil.html", os.path.join("exploits", "neon_skies", "evil.html")),
    ("s.js", os.path.join("exploits", "neon_skies", "s.js")),
    ("server.py", os.path.join("exploits", "neon_skies", "server.py")),
]

for src_name, dst_rel in moves:
    src_path = os.path.join(WORKSPACE, src_name)
    dst_path = os.path.join(WORKSPACE, dst_rel)
    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
        print(f"[+] Moved: {src_name} -> {dst_rel}")
    else:
        print(f"[-] Source file does not exist (may already be moved): {src_path}")

# 3. Remove junk files
junk = ["test.txt", "public.zip"]
for j in junk:
    j_path = os.path.join(WORKSPACE, j)
    if os.path.exists(j_path):
        os.remove(j_path)
        print(f"[+] Removed junk file: {j}")

# 4. Update image paths in writeups
writeups_dir = os.path.join(WORKSPACE, "writeups")
for fname in os.listdir(writeups_dir):
    if fname.endswith(".md"):
        fpath = os.path.join(writeups_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace (images/ with (../images/ and src="images/ with src="../images/
        updated = re.sub(r'\]\(images/', '](../images/', content)
        updated = re.sub(r'src=["\']images/', 'src="../images/', updated)

        if updated != content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(updated)
            print(f"[+] Updated image paths to ../images/ in {fname}")
        else:
            print(f"[-] No image path changes needed in {fname}")

print("\n[✓] Workspace reorganization completed successfully!")
