from pydantic import BaseModel, Field
from typing import List
import pathlib
import sys

from agent_smith.sandbox.guards.exceptions import FilesystemRestrictedError


class FilesystemGuard(BaseModel):
    allowed_directories: List[str]
    audit_event: List[str] = Field(
        default=[
            "open",
            "os.add_dll_directory",
            "os.chdir",
            "os.chflags",
            "os.chmod",
            "os.chown",
            "os.exec",
            "os.getxattr",
            "os.listdir",
            "os.listxattr",
            "os.mkdir",
            "os.posix_spawn",
            "os.remove",
            "os.removexattr",
            "os.rmdir",
            "os.scandir",
            "os.setxattr",
            "os.startfile",
            "os.startfile/2",
            "os.utime"
        ]
    )

    def __hook_filesystem_event(self, event, args) -> None:
        if event in self.audit_event and not self.is_allowed(args[0]):
            raise FilesystemRestrictedError(
                f"The sandbox boundaries are {self.allowed_directories}, "
                f"you can not access {args[0]}.")

    def is_allowed(self, path: str) -> bool:
        p = pathlib.PurePath(path)
        for d in self.allowed_directories:
            if p.is_relative_to(d):
                return True
        return False

    def install(self) -> None:
        sys.addaudithook(self.__hook_filesystem_event)
