from agent_smith.mcp.server import create_server


def main():
    server = create_server("Agent Smith", None)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
