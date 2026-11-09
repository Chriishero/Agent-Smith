import asyncio
from mcp.client import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from test import mcp


async def main():
    server = StdioServerParameters(command="uv", args=["run", "test.py"])
    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            print(result.tools)

if __name__ == "__main__":
    asyncio.run(main())