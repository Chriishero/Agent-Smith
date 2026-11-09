from pydantic import BaseModel, Field, PrivateAttr, model_validator
from typing import Dict, Any, Callable, Optional
from resource import RLIMIT_AS

from agent_smith.sandbox.SandboxConfig import SandboxConfig
from agent_smith.sandbox.guards.imports import ImportsGuard
from agent_smith.sandbox.guards.filesystem import FilesystemGuard
from agent_smith.sandbox.guards.network import NetworkGuard
from agent_smith.sandbox.guards.limit import LimitGuard
from agent_smith.sandbox.guards.builtins import allowed_builtins_dict


class Namespace(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }
    config: SandboxConfig = Field(default_factory=SandboxConfig)

    __imports_guard: ImportsGuard = PrivateAttr()
    __filesystem_guard: FilesystemGuard = PrivateAttr()
    __network_guard: NetworkGuard = PrivateAttr()
    __limit_guard: LimitGuard = PrivateAttr()
    __namespace_dict: Dict[str, Any] = PrivateAttr()

    @model_validator(mode="after")
    def validator(self) -> "Namespace":
        self.__imports_guard = ImportsGuard(
            authorized_imports=self.config.authorized_imports
        )
        self.__filesystem_guard = FilesystemGuard(
            allowed_directories=self.config.allowed_directories
        )
        self.__network_guard = NetworkGuard()
        self.__limit_guard = LimitGuard(
            resource=RLIMIT_AS, max_memory_mb=self.config.max_memory_mb
        )

        return self

    @property
    def namespace_dict(self) -> Dict[str, Any]:
        return self.__namespace_dict

    def build(self, tools: Optional[Dict[str, Callable]]) -> Dict[str, Any]:
        self.__filesystem_guard.install()
        self.__network_guard.install()
        self.__limit_guard.install()

        builtins = dict(allowed_builtins_dict)
        builtins["__import__"] = self.__imports_guard.import_module
        self.__namespace_dict = {
            "__name__": "__sandbox__",
            "__builtins__": builtins,
        }
        if tools is not None:
            self.__namespace_dict.update(tools)

        return self.__namespace_dict
