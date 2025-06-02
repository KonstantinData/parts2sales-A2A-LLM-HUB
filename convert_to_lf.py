import os

# Dateiendungen, die behandelt werden sollen
target_extensions = (".py", ".yaml", ".yml", ".json")

# Starte im aktuellen Verzeichnis
base_path = "."


def convert_file_to_lf(filepath):
    try:
        with open(filepath, "rb") as f:
            content = f.read()

        # Nur konvertieren, wenn CRLF vorhanden ist
        if b"\r\n" in content:
            new_content = content.replace(b"\r\n", b"\n")
            with open(filepath, "wb") as f:
                f.write(new_content)
            print(f"Konvertiert: {filepath}")
        else:
            print(f"Übersprungen (bereits LF): {filepath}")
    except Exception as e:
        print(f"Fehler bei {filepath}: {e}")


for root, dirs, files in os.walk(base_path):
    for filename in files:
        if filename.endswith(target_extensions):
            full_path = os.path.join(root, filename)
            convert_file_to_lf(full_path)
