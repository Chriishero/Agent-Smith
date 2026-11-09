from mcp.server import MCPServer

mcp = MCPServer("test")

@mcp.tool()
def add(a: int, b: int) -> int:
	"""ouaf ouaf"""
	return a + b

if __name__ == "__main__":
	mcp.run()