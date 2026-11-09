from pydantic import BaseModel, Field
from typing import List
import importlib
from importlib import util
from types import ModuleType
import ast

from agent_smith.sandbox.guards.exceptions import (
    SandboxSecurityViolation, ModuleNotAuthorizedError
)


class ImportsGuard(BaseModel):
    authorized_imports: List[str]

    def import_module(self, name, *args, **kwargs) -> ModuleType:
        if self.__is_authorized(name) is True:
            return importlib.import_module(name)
        else:
            raise SandboxSecurityViolation(
                f"'{name}' import is not authorized."
            )

    def __is_authorized(self, module: str) -> bool:
        if module in self.authorized_imports:
            return True
        elif '.' in module:
            prefix = '.' if module[0] == '.' else ''
            for alias in module.split('.')[::-1]:
                tmp = prefix + module[:-(len(alias) + 1)]
                if tmp + '.*' in self.authorized_imports:
                    return True
        return False

    @staticmethod
    def collect_imports_from_code(source: str) -> List[str]:
        imports: List[str] = []
        ast_object = ast.parse(source)

        for node in ast.walk(ast_object):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                prefix = '.' * node.level + (node.module or '')
                for alias in node.names:
                    try:
                        tmp = util.find_spec(prefix + '.' + alias.name)
                        if tmp is not None:
                            imports.append(prefix + '.' + alias.name)
                        else:
                            raise ModuleNotAuthorizedError()
                    except (ModuleNotFoundError, ModuleNotAuthorizedError):
                        imports.append(prefix)

        return imports
