"""
archive_utils.py

Purpose : Utilities for archiving prompt/config files with timestamped backups.
Version : 0.1.0-raw
Author  : Konstantin & AI Copilot
Notes   :
- Uses shutil for file operations
- Raises if target/archive dir missing
- Example: archive_prompt_file('prompts/my_template.json')
"""

import os
import shutil
from datetime import datetime


def archive_prompt_file(file_path: str, archive_dir: str = "archive") -> str:
    """
    Archive a prompt file to the specified archive directory with timestamp.

    Args:
        file_path (str): Path to the file to archive.
        archive_dir (str): Directory where the archive will be stored.

    Returns:
        str: Path to the archived file.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.path.isdir(archive_dir):
        os.makedirs(archive_dir)
    base_name = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_file = os.path.join(archive_dir, f"{base_name}.{timestamp}.bak")
    shutil.copy2(file_path, archived_file)
    return archived_file
