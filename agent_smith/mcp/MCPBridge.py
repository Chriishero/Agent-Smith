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
    __loop: AbstractEventLoop = PrivateAttr()
    __session: ClientSession = PrivateAttr()
    __tools: Dict[str, Callable] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def validator(self) -> "MCPBridge":
        self.__thread = threading.Thread(target=self.__thread_function)
        self.__thread.start()
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
            print(e)

    async def __start(self) -> None:
        async with stdio_session(self.command, self.args) as session:
            self.__session = session
            tools = await session.list_tools()
            for tool in tools.tools:
                name = tool.name
                ordre = tool.input_schema["required"]
                doc = tool.description
                self.__tools[name] = self.__make(name, ordre, doc)

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
        result = future.result(timeout=5)
        if result.is_error is True:
            raise RuntimeError(result)
        return "".join([c.text for c in result.content if hasattr(c, "text")])
