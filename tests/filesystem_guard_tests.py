from agent_smith.sandbox.guards.filesystem import FilesystemGuard


g = FilesystemGuard(authorized_directories=["test/test1", "test/test2"])
g.install()

with open("test/test1/b.md", "r") as f:
    f.read()
