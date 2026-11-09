from typing import Dict

from agent_smith.tools.filesystem import list_files


def search_code(pattern: str, file_pattern: str) -> Dict[str, Dict[int, str]]:
    splitted_path = file_pattern.replace("\\", '/').split("/")
    directory = "/".join(splitted_path[:-1])
    files = list_files(directory, splitted_path[-1])

    return {}


def search_function_or_class_definition_in_code(name: str):
    pass


def find_references(name: str, filepath: str, line: int):
    pass
