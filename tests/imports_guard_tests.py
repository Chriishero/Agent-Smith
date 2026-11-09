import os
import subprocess
from agent_smith.sandbox.guards.imports import ImportsGuard


authorized = [
        "math", "math.*",
        "collections", "collections.*",
        "itertools", "re", "json",
        "typing", "typing.*",
        "functools", "operator",
        "heapq", "bisect", "copy",
        "string", "random",
        "datetime", "datetime.*",
        "array", "cmath",
        "agent_smith.*"
]

guard = ImportsGuard(authorized_imports=authorized)

content = ""
with open("test.py", 'r') as f:
    content = f.read()

imports = guard.collect_imports_from_code(content)

for m in imports:
    try:
        guard.import_module(m)
        print(m, "has been imported")
    except Exception as e:
        print(e)
