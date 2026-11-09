from pydantic import BaseModel, Field, PrivateAttr, model_validator
from typing import Dict, Any, Callable
import ast

from agent_smith.sandbox.SandboxConfig import SandboxConfig
from agent_smith.sandbox.Namespace import Namespace
from agent_smith.sandbox.guards.exceptions import SandboxSecurityViolation


class Sandbox(BaseModel):
    config: SandboxConfig = Field(default_factory=SandboxConfig)
    tools: Dict[str, Callable] = Field(default_factory=dict)

    __namespace_dict: Dict[str, Any] = PrivateAttr()

    @model_validator(mode="after")
    def validator(self) -> "Sandbox":
        self.__namespace_dict = Namespace(
            config=self.config
        ).build(self.tools)

        return self

    def start(self, source: str):
        try:
            tree = ast.parse(
                source=source, mode="exec"
            )
            code = compile(source=tree, filename='<sandbox>', mode='exec')
            exec(code, self.__namespace_dict)
        except SandboxSecurityViolation as e:
            return (type(e).__name__, e)
        except Exception as e:
            return (type(e).__name__, e)
        return ("ok", None)
