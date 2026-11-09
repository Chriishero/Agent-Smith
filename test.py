from agent_smith.mcp.MCPBridge import MCPBridge
import time

bridge = MCPBridge(command="uv", args=["run", "server_test.py"])
time.sleep(5)
add = bridge.tools["add"]
print(add(a=1, b=3))
