Agent Smith note:

- code-based tool calling approach: the LLM will generate python code such as:
    result = search_code("validate_email")
    print(result)
    content = read_file("models.py", 1, 50)
    print(content)
    
    The tool calling will be perform directly into the code, calling tools/functions
    
- the agent must support multiple LLM providers and models: it must be generic
- usage tracking of the LLM must be implemented (token, retries, latency, requests)
- the tools must be independent of the agent loop
- multi-agent architecture is allowed
- docker sandbox in python using the lib 'docker' and the function 'exec'


ALREADY IMPLEMENTED:
1. Sandbox
    - sandbox/cli.py/main():
        - use 'argparse' to implement a cli with 3 possible arguments: config (path to a SandboxConfig json file), --mcp-stdio (MCP server over stdio, ex: 'python mcp_tools.py), --mcp-server (MCP server over HTTP)
        - handle error for the 3 all arguments
        - loop for the sandbox prompt line
            - handle skip line
            - handle 'exit' command
            - handle any python prompt:
                - check if complete with 'codeop.compile_command(source)' where source = "\n".join(prompt)
                - if it is complete, run it with SandboxRunner(config, mcp_spec).run(source) where mcp_spec is the python file(s) from --mcp-stdio
            - print any error, final response or python code output
    - models/config.py/SandboxConfig:
        - authorized_imports
        - allowed_directory
        - max_execution_time_seconds
        - max_memory_mb
    - sandbox/runner.py/SandboxRunner:
        - use 'multiprocessing' module
        - run(self):
            - check if the process (where the Sanbox will be run) is alive with '_is_alive()' (if self.process is None or not).
                - if not alive, self._restart() it
                    - terminate the process
                    - start(self)
                        - create two connections: parent_conn, child_conn = multiprocessing.Pipe() (child_conn is the start of the pipe, parent_conn is the end)
                        - create the worker = SandboxWorker(self.config, self.mcp_spec): will execute code in the Sandbox
                        - create the process = multiprocessing.Process(target=worker.run, args=(child_conn,)) where target is the function to run and args its arguments
                        - run the process then self.connection = parent_conn
                - send the code from self.connection
                    - start the process target with child_conn: worker.run(child_conn)
                        - create the sandbox = Sandbox(self.config, tools)
                - return whether there is any data to be read within the timeout time (bool): self.connection.poll(timeout)
                    - if not, restart the process with self._restart()
                    - return an error self._error_results(kind, message) where 'kind' is 'TimeoutError'
                - try to receive the code result from parent_conn (send by child_conn in the process target) and return it
    - sandbox/runner.py/SandboxWorker:
        - config: configuration of the sandbox (SandboxConfig)
        - mcp_spec: tuple of the python interpreter (ex: python3) and the file MCP tools (ex: mcp_tools.py): the MCP server to launch
        - run(self, connection):
            - install the guards for the maximum memory mb available in the sandbox: LimitsGuard(self.config, self.mcp_spec)
            - if mcp_spec exist (not None):
                - create a bridge = McpBridge(*self.mcp_spec) between the tool(s) call in the sandbox (synchronous) and the actual MCP tools (asynchronous)
                - get the tools = bridge.tools
            - create a sandbox = Sandbox(self.config, tools)
            - while True:
                - the target will try to receive the code with connection
                - if code is None: break
                - result = self._execute(sandbox, code): execute the code in the sandbox
                    - return result = sandbox.sandbox_start(code)
                - send the result from connection to the other end of the pipe
            - bridge.close()
    - sandbox/mcp_bridge.py/McpBridge:
        - self.command: command to run (ex: python3)
        - self.args: MCP server file (via stdio) to interpret (ex: [mcp_tools.py])
        - event intern to the thread: self.ready = threading.Event()
        - create a thread for the MCP server: thread = threading.Thread(target=self._thread)
        - thread.start()
        - wait maximum 30s until the MCP is ready (self.ready flag set to True): if not self.ready.wait(30), then raise RuntimeError("...")
        - _thread(self):
            - create a new event loop where all the asynchrone function will be run: self.loop = asyncio.new_event_loop()
            - into the current thread (MCP server thread), set the event loop as: asyncio.set_event_loop(self.loop)
            - self.loop.run_until_complete(self._main())
            - awake the MCP thread (set its flag to True): self.ready.set()
        - async _main(self): coroutine (object representing an asynchronous operation) executed by the event loop
            - stop event: self.stop = asyncio.Event()
            - launch 'self.command self.args' as a subprocess running the MCP server over stdio: async with stdio_session(self.command, self.args) as self.session:
                - ask the MCP server for the tools and continue _main() when the result is available: listed = await session.list_tools()
                - for each tool in listed.tools:
                    - transform the MCP tool into a Python function usable for the sandbox: self.tools[tool.name] = self._make(tool.name, order, tool.description)
                at this step, self.tools = {"read_file": <wrapper>, "edit_file": <wrapper>, ...}
            - awake the main thread (set its flag to True): self.ready.set()
            - wait until the _main() coroutine stop: await self.stop.wait()
        - _make(self, name, order, doc):
            - define a wrapper(*args, **kwargs): the function that will be call by the sandbox
                - create a dict params = dict(zip(order, args)) that map the tool arguments with their names ({arg_name: arg, ...})
                - add/replace the named parameters: params.update(kwargs)
                - return the output of the tool: return self._call(name, params)
            - change the name of the wrapper to the target tool name: wrapper.__name__ = name
            - same for the documentation: wrapper.__doc__ = doc
            - return the new function 'wrapper'
        - _call(self, name, params):
            - create a coroutine = self.session.call_tool(name, params) that represent an asking to the MCP server to execute the tool 'name' with 'params'
            - create a future (result of an unfinished operation) = asyncio.run_coroutine_threadsafe(coro, self.loop) in the event loop of the MCP thread
            - wait the result of the future for max 60s: result = future.result(timeout=60)
            - extract the text = "".join(block.text for block in result.content if hasattr(block, "text"): an textual representation of the MCP response
            - handle error
            - return text
    - sandbox/sandbox.py/Sandbox:


ressources:
- https://www.youtube.com/watch?v=sL_syMmRkoU
- https://blog.stephane-robert.info/docs/developper/programmation/python/agents-sandbox/
- https://medium.com/@Shrishml/making-our-own-code-interpreter-part-1-making-of-a-sandbox-382da3339eaa
- https://stackoverflow.com/questions/50974960/whats-the-difference-between-docker-and-python-virtualenv
- https://docs.python.org/3/library/argparse.html
- https://docs.python.org/3/library/multiprocessing.html
- https://docs.python.org/3/library/asyncio.html
- https://docs.python.org/3/library/ast.html
- https://peps.python.org/pep-0578/
- https://docs.python.org/3/library/audit_events.html
- https://docs.python.org/3/library/os.html
- https://docs.python.org/3/library/sys.html
- https://docs.python.org/3/library/resource.html
- https://docs.python.org/fr/3/library/threading.html#threading.Thread
- https://stackoverflow.com/questions/2220699/whats-the-difference-between-eval-exec-and-compile
- https://nedbatchelder.com/blog/201206/eval_really_is_dangerous
- https://stackoverflow.com/questions/15197673/using-pythons-eval-vs-ast-literal-eval
- https://py.sdk.modelcontextprotocol.io/