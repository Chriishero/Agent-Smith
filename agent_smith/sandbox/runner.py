from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Tuple, Optional
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection

from agent_smith.sandbox.SandboxConfig import SandboxConfig
from agent_smith.sandbox.exceptions import (
    SandboxTimeoutError
)
from agent_smith.sandbox.Sandbox import Sandbox
from agent_smith.mcp.MCPBridge import MCPBridge


class SandboxRunner(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }
    config: SandboxConfig = Field(default_factory=SandboxConfig)
    mcp_params: Optional[Tuple[str, List[str]]]

    __process: Process = PrivateAttr()
    __connection: Connection = PrivateAttr()

    def __create(self) -> None:
        parent, child = Pipe()
        self.__connection = parent
        self.__process = Process(target=self.__worker, args=(child,))
        self.__process.start()

    def __worker(self, connection: Connection) -> None:
        try:
            tools = None
            if self.mcp_params is not None:
                bridge = MCPBridge(*self.mcp_params)
                tools = bridge.tools
            sandbox = Sandbox(config=self.config, tools=tools)
            while True:
                try:
                    source = connection.recv()
                    if source is None:
                        break
                    res = sandbox.start(source)
                    connection.send(res)
                except KeyboardInterrupt as e:
                    connection.send(("ok", e))
        finally:
            connection.close()

    def run(self, source: str | None) -> None:
        self.__connection.send(source)
        timeout = self.config.max_execution_time_seconds
        if not self.__connection.poll(timeout):
            raise SandboxTimeoutError(
                f"The execution take more than {timeout} seconds"
            )
        status, res = self.__connection.recv()

        if status != "ok":
            print(f"{status}:", res)

    def close(self) -> None:
        if self.__process.is_alive():
            self.__connection.send(None)
            self.__process.join()
        self.__connection.close()

    def __enter__(self) -> "SandboxRunner":
        self.__create()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
