"""
Shared utilities for build scripts
"""

import subprocess
import sys
from pathlib import Path


def safe_file_read(file_path: Path) -> str:
    """Safely read file with proper error handling"""
    try:
        return file_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Failed to read {file_path}: {e}")


def safe_file_write(file_path: Path, content: str) -> None:
    """Safely write file with proper error handling"""
    try:
        file_path.write_text(content, encoding='utf-8')
    except IOError as e:
        raise IOError(f"Failed to write {file_path}: {e}")


def run_script(script_path: Path) -> None:
    """Run Python script with error handling"""
    subprocess.run([sys.executable, str(script_path)], check=True)


def ensure_dir(file_path: Path) -> None:
    """Ensure parent directory exists"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
