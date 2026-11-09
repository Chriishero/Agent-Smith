from pydantic import BaseModel, Field, PrivateAttr, model_validator
from mcp.client import ClientSession
from typing import Dict, Callable, List, Optional, AsyncGenerator
import asyncio
from asyncio import AbstractEventLoop
import threading

from agent_smith.mcp.client import call_tool


class MCPBridge(BaseModel):
    commands: str = Field(min_length=1)
    args: List[str]

    __thread: threading.Thread = PrivateAttr()
    __session: AsyncGenerator[ClientSession] = PrivateAttr()
    __tools: Optional[Dict[str, Callable]] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def validator(self) -> "MCPBridge":
        self.___thread = threading.Thread(target=self.__start)
        self.__thread.start()
        return self

    @property
    def tools(self) -> Optional[Dict[str, Callable]]:
        return self.__tools

    def __thread(self):
        try:
			asyncio.run(self.__start())
        except Exception as e:
			print(e)

	def __make(self, name: str, **kwargs) -> Callable:
        def wrapper(name: str, **kwargs) -> str:
			

    def __call(self, name: str, **kwargs) -> str:
        result = self.__session.call_tool(name=name, params=kwargs)
        return "".join([c.text for c in result.content if hasattr(c, "text")])
        
        
