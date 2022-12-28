"""Calibre executable IO module."""

import subprocess
from pathlib import Path

from .config import settings


def convert_ebook(book_path: str, to: str = "azw3") -> Path:
    """Converts an ebook to a different format using the calibre executable"""
    
    print(f"Converting {book_path!r} to {to!r}")
    input_file = Path(book_path)
    output_file = input_file.parent / f"{input_file.stem}.{to}"

    cmd = [settings.calibre_executable, input_file.as_posix(), output_file.as_posix()]
    subprocess.check_output(cmd)
    return output_file
