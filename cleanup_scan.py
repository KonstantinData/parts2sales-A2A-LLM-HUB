import os
import re

REPO_ROOT = "Pfad/zu/deinem/Projekt"  # Passe das ggf. an, z.B. "./" oder absolut

old_import_patterns = [
    r"from\s+utils\.event_logger\s+import",
    r"import\s+utils\.event_logger",
]
old_log_dirs = [
    "logs/quality_check",
    "logs/controller_decision",
    "logs/prompt_improvement",
    "data/outputs",
]
old_open_patterns = [r'open\s*\(\s*[\'"]logs/', r'open\s*\(\s*[\'"]data/outputs']

results = []

for dirpath, _, filenames in os.walk(REPO_ROOT):
    for fname in filenames:
        if fname.endswith(".py"):
            fpath = os.path.join(dirpath, fname)
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                # Suche nach alten Imports
                for pat in old_import_patterns:
                    if re.search(pat, line):
                        results.append((fpath, idx, "OLD IMPORT", line.strip()))
                # Suche nach direkten Dateischreibzugriffen
                for pat in old_open_patterns:
                    if re.search(pat, line):
                        results.append(
                            (fpath, idx, "DIRECT LOG/OUTPUT OPEN", line.strip())
                        )

print("\n=== Old Imports / Direct Output Access ===")
for r in results:
    print(f"{r[0]}:{r[1]} [{r[2]}]  {r[3]}")

print(
    "\n=== Files/Dirs matching old log/output patterns (to archive/remove if empty) ==="
)
for old_dir in old_log_dirs:
    abs_path = os.path.join(REPO_ROOT, old_dir)
    if os.path.exists(abs_path):
        print(f"Exists: {abs_path}")
