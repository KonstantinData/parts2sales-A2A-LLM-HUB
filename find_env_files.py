import os


def find_dotenv_files(root_dir="."):
    """
    Recursively find all files starting with '.env' in the project directory tree.
    Prints the full path for each found .env file.
    """
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith(".env"):
                filepath = os.path.join(subdir, file)
                print(filepath)


if __name__ == "__main__":
    find_dotenv_files(".")
