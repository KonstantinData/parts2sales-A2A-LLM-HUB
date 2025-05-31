import shutil
from pathlib import Path


def clear_logs(logs_path: str = "logs"):
    logs_dir = Path(logs_path)
    if logs_dir.exists() and logs_dir.is_dir():
        for subdir in logs_dir.iterdir():
            if subdir.is_dir():
                # Alle Dateien in Unterordner löschen
                for file in subdir.iterdir():
                    if file.is_file():
                        file.unlink()
                # Optional: Wenn du die Unterordner auch löschen willst, dann statt oben:
                # shutil.rmtree(subdir)
        print(f"Cleared all files inside {logs_dir}")
    else:
        print(f"{logs_path} does not exist or is not a directory")


if __name__ == "__main__":
    clear_logs()
