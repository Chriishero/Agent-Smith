import argparse
import json

from agent_smith.sandbox.exceptions import (
    ArgumentNotAllowedError, SandboxQuittingException
)
from agent_smith.sandbox.SandboxConfig import SandboxConfig
from agent_smith.sandbox.runner import SandboxRunner


def main() -> None:
    try:
        parser = argparse.ArgumentParser(prog="Agent Smith")

        parser.add_argument(
            "sandbox_configuration",
            default=None,
            nargs="?",
            help="Custom configuration JSON file for the sandbox."
        )
        parser.add_argument(
            "--mcp-stdio",
            default=None,
            help="MCP server over stdio (ex: python mcp_tools.py)",
        )
        parser.add_argument(
            "--mcp-server",
            default=None,
            help="URL to the MCP server.",
        )

        args = parser.parse_args()
        if args.sandbox_configuration is not None:
            try:
                with open(args.sandbox_configuration, "r") as f:
                    config = SandboxConfig(**json.load(f))
            except (FileNotFoundError, PermissionError) as e:
                print(e)
                return
        else:
            config = SandboxConfig()

        if args.mcp_stdio and args.mcp_server:
            raise ArgumentNotAllowedError(
                "'mcp-server' argument is not allowed when \
                'mcp-stdio' is specified"
            )
        if args.mcp_stdio is not None:
            pass

        elif args.mcp_server is not None:
            pass

        tools = {}

        with SandboxRunner(config=config, tools=tools) as runner:
            conditional_block = 0
            source = ""
            while True:
                try:
                    if conditional_block > 0:
                        indent = "    " * conditional_block
                        tmp = input("..." * conditional_block + indent)
                        if not tmp:
                            conditional_block -= 1
                        else:
                            source += "\n" + indent + tmp
                    if not source:
                        source = input(">>> ")
                    if source.endswith(":"):
                        conditional_block += 1
                        continue
                    elif source in ("exit()", "quit()"):
                        raise SandboxQuittingException()
                    elif source in ("exit", "quit"):
                        print(f"Use {source}() or Ctrl-D (i.e. EOF) to exit")
                        source = ""
                    elif source and conditional_block == 0:
                        runner.run(source)
                        source = ""
                except (SandboxQuittingException):
                    break
                except EOFError:
                    print()
                    break
                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt")
    except Exception as e:
        print(e)
