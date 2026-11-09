import contextlib
from typing import List, AsyncGenerator
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client import ClientSession


@contextlib.asynccontextmanager
async def stdio_session(
    command: str, args: List[str]
        ) -> AsyncGenerator[ClientSession, None]:
    server = StdioServerParameters(command=command, args=args)
    async with stdio_client(server=server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session
