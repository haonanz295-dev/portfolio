from pathlib import Path
import hashlib
import json
import sys
root = Path(__file__).resolve().parent
manifest = json.loads((root / "SHA256SUMS.json").read_text(encoding="utf-8"))
failed = []
for name, expected in manifest.items():
    path = root / name
    ok = path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected
    print(("OK   " if ok else "FAIL ") + name)
    if not ok:
        failed.append(name)
sys.exit(1 if failed else 0)
