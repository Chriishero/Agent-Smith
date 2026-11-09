from typing import List
from mcp.types import CallToolResult, ListToolsResult

from agent_smith.mcp.stdio_session import stdio_session


async def call_tool(
    command: str, args: List[str], name: str, **kwargs
        ) -> CallToolResult:
    async with stdio_session(command, args) as session:
        return await session.call_tool(name=name, arguments=kwargs)


async def list_tools(command: str, args: List[str]) -> ListToolsResult:
    async with stdio_session(command, args) as session:
        return await session.list_tools()
