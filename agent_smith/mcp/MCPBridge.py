from pydantic import BaseModel, Field, PrivateAttr, model_validator
from mcp.client import ClientSession
from typing import Dict, Callable, List, Optional, AsyncGenerator
import asyncio
from asyncio import AbstractEventLoop
import threading

from agent_smith.mcp.client import call_tool, list_tools
from agent_smith.mcp.stdio_session import stdio_session


class MCPBridge(BaseModel):
    command: str = Field(min_length=1)
    args: List[str] = Field(min_length=1)

    __thread: threading.Thread = PrivateAttr()
    __ready: threading.Event = PrivateAttr()
    __stop: asyncio.Event = PrivateAttr()
    __error: str = PrivateAttr()
    __loop: AbstractEventLoop = PrivateAttr()
    __session: ClientSession = PrivateAttr()
    __tools: Dict[str, Callable] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def validator(self) -> "MCPBridge":
        self.__ready = threading.Event()
        self.__thread = threading.Thread(target=self.__thread_function)
        self.__thread.start()
        if not self.__ready.wait(30):
            raise RuntimeError("MCP server did not start.")
        if self.__error is not None:
            raise RuntimeError(f"MCP server failed to start: {self.__error}")
        return self

    @property
    def tools(self) -> Optional[Dict[str, Callable]]:
        return self.__tools

    def __thread_function(self) -> None:
        try:
            self.__loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__loop)
            self.__loop.run_until_complete(self.__start())
        except Exception as e:
            self.__error = f"{type(e).__name__}: {e}"
            self.__ready.set()

    async def __start(self) -> None:
        self.__stop = asyncio.Event()
        async with stdio_session(self.command, self.args) as session:
            self.__session = session
            tools = await session.list_tools()
            for tool in tools.tools:
                name = tool.name
                ordre = tool.input_schema["required"]
                doc = tool.description
                self.__tools[name] = self.__make(name, ordre, doc)
            self.__ready.set()
            await self.__stop.wait()

    def __make(
            self, name: str, ordre: List[str], doc: Optional[str]
            ) -> Callable:
        def wrapper(*args, **kwargs) -> str:
            params = dict(zip(ordre, args))
            params.update(**kwargs)
            return self.__call(name=name, **params)
        wrapper.__name__ = name
        wrapper.__doc__ = doc

        return wrapper

    def __call(self, name: str, **kwargs) -> str:
        print("create corroutien")
        coroutine = self.__session.call_tool(
            name=name, arguments=kwargs
        )
        print("create future")
        future = asyncio.run_coroutine_threadsafe(coroutine, self.__loop)
        print("result")
        result = future.result(timeout=60)
        if result.is_error is True:
            raise RuntimeError(result)
        return "".join([c.text for c in result.content if hasattr(c, "text")])

    def close(self) -> None:
        if self.__loop is not None and self.__stop is not None:
            self.__loop.call_soon_threadsafe(self.__stop.set)
