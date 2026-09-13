import zipfile
import traceback

with zipfile.ZipFile('hunting-01-player.zip') as z:
    try:
        with z.open('artefact.zip', pwd=b'infected') as src:
            with open('artefact.zip', 'wb') as dst:
                total = 0
                while True:
                    chunk = src.read(1024 * 1024 * 16) # 16MB
                    if not chunk:
                        break
                    dst.write(chunk)
                    total += len(chunk)
                    print(f"Extracted {total / 1024 / 1024:.1f} MB...")
    except Exception as e:
        print("Exception:", e)
        traceback.print_exc()
