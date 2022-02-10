import subprocess
from pathlib import Path

from .config import EXEC


def convert_ebook(book_path: str, to: str = "azw3"):
    print(f"Converting {book_path!r} to {to!r}")
    input_file = Path(book_path)
    output_file = input_file.parent / f"{input_file.stem}.{to}"

    cmd = [EXEC, input_file.as_posix(), output_file.as_posix()]
    subprocess.check_output(cmd)
    return output_file
