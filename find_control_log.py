import os


def find_control_log_usages(root_dir="."):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(subdir, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if "control_log" in line:
                            print(f"{filepath}:{i}: {line.strip()}")


if __name__ == "__main__":
    find_control_log_usages()
