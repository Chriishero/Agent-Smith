import sys

from agent_smith.sandbox.guards.exceptions import (
    NetworkAccessNotAuthorizedError
)


class NetworkGuard:
    def __hook_network_event(self, event: str, args) -> None:
        if event.startswith("socket."):
            raise NetworkAccessNotAuthorizedError(
                "Network access is not authorized in the sandbox"
            )

    def install(self) -> None:
        sys.addaudithook(self.__hook_network_event)
