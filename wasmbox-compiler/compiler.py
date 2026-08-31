import wasmtime

RESTRICTED_IMPORTS = {"os", "socket", "subprocess", "sys", "shutil", "ctypes"}

def validate_python_code(source_code: str) -> tuple[bool, str | None]:
    """
    Basic static check for restricted imports before compilation.
    Returns (is_valid, error_message).
    """
    import ast

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in RESTRICTED_IMPORTS:
                    return False, f"Restricted import not allowed: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in RESTRICTED_IMPORTS:
                return False, f"Restricted import not allowed: {node.module}"

    return True, None

def run_python_plugin(source_code: str) -> dict:
    """
    Executes untrusted Python source code inside a WASI-sandboxed
    CPython interpreter running in Wasmtime.
    Returns a dict with captured stdout, stderr, and success status.
    """
    is_valid, validation_error = validate_python_code(source_code)
    if not is_valid:
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": validation_error,
        }
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)

    wasi_config = wasmtime.WasiConfig()
    wasi_config.argv = ["python", "-c", source_code]

    wasi_config.stdout_file = "plugin_stdout.txt"
    wasi_config.stderr_file = "plugin_stderr.txt"
    wasi_config.preopen_dir(".", "/")
    store.set_wasi(wasi_config)

    linker = wasmtime.Linker(engine)
    linker.define_wasi()

    module = wasmtime.Module.from_file(engine, "python.wasm")
    instance = linker.instantiate(store, module)

    success = True
    error_message = None
    try:
        start = instance.exports(store)["_start"]
        start(store)
    except Exception as e:
        success = False
        error_message = str(e)

    with open("plugin_stdout.txt", "r") as f:
        stdout = f.read()
    with open("plugin_stderr.txt", "r") as f:
        stderr = f.read()

    return {
        "success": success,
        "stdout": stdout,
        "stderr": stderr,
        "error": error_message,
    }