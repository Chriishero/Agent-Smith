from typing import Optional, Dict, List
from mcp.server import MCPServer

from agent_smith.tools.filesystem import read_file, edit_file, list_files
from agent_smith.tools.codesearch import (
    search_code, search_function_or_class_definition_in_code, find_references
)
from agent_smith.tools.execution import (
    run_tests, get_patch, run_command
)


def create_server(name: str, url: Optional[str]):
    server = MCPServer(name=name, website_url=url)

    @server.tool(name="read_file")
    def read_file_tool(
        filepath: str, start_line: int, end_line: int
    ) -> Dict[int, str]:
        return read_file(filepath, start_line, end_line)

    @server.tool(name="edit_file")
    def edit_file_tool(
        filepath: str, old_str: str, new_str: str
    ) -> str:
        return edit_file(filepath, old_str, new_str)

    @server.tool(name="list_files")
    def list_files_tool(directory: Optional[str], pattern: str) -> List[str]:
        return list_files(directory, pattern)

    @server.tool(name="search_code")
    def search_code_tool(
            pattern: str, file_pattern: str
    ) -> Dict[str, Dict[int, str]]:
        return search_code(pattern, file_pattern)

    @server.tool(name="search_function_or_class_definition_in_code")
    def search_function_or_class_definition_in_code_tool(name: str):
        return search_function_or_class_definition_in_code(name)

    @server.tool(name="find_references")
    def find_references_tool(name: str, filepath: str, line: int):
        return find_references(name, filepath, line)

    return server
