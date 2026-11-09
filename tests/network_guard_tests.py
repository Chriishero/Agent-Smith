import socket
from agent_smith.sandbox.guards.network import NetworkGuard
import sys


g = NetworkGuard()
g.install()

print("yes")
print(socket.gethostname())