from typing import Dict, Optional, List
import pathlib


def read_file(
        filepath: str, start_line: int, end_line: int
        ) -> Dict[int, str]:
    res = {}
    try:
        with open(filepath, "r") as f:
            c = f.read()
            lines = c.splitlines()
            for i in range(start_line, end_line, 1):
                res[i] = lines[i]
    except Exception as e:
        print(e)

    return res


def edit_file(
        filepath: str, old_str: str, new_str: str
        ) -> str:
    new = ""
    try:
        with open(filepath, "r") as f:
            c = f.read()
            new = c.replace(old_str, new_str)
    except Exception as e:
        print(e)

    return new


def list_files(directory: Optional[str], pattern: str) -> List[str]:
    if not directory:
        directory = '.'
    p = pathlib.Path(directory)

    return [str(f) for f in p.glob(pattern)]
